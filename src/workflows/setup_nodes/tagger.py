"""Creates tags for a novels input"""

import logging
import numpy as np
import scipy.sparse as ss
import matplotlib.pyplot as plt
import corextopic.corextopic as ct
import corextopic.vis_topic as vt
from collections import Counter
from src.providers import LLMProvider, NLPProvider
from sklearn.feature_extraction.text import CountVectorizer
from typing import List
from src.workflows.states import SetupState

logger = logging.getLogger(__name__)


class Tagger:
    def __init__(self, llm_provider: LLMProvider, nlp_provider: NLPProvider):
        self.llm_provider = llm_provider
        self.nlp_provider = nlp_provider
        logger.debug("Tagger initialized with shared NLP provider")

    def tag_text(self, state: SetupState) -> List[str]:
        """
        Args:
            state: Current setup state

        Returns:
            List of tags (strings) from the text
        """
        chapters: List[str] = state["all_chapters"]
        logger.debug("Processing %d chapters for tagging", len(chapters))
        
        documents_nouns_only = [self._extract_nouns_from_text(chapter) for chapter in chapters]
        logger.debug("Extracted nouns from chapters: %s", documents_nouns_only[:3])  # Show first 3 for debugging
        
        # Check if we have any content after noun extraction
        total_content = " ".join(documents_nouns_only).strip()
        if not total_content:
            logger.warning("No nouns extracted from chapters, returning empty tag list")
            return []
        
        # Check if we have enough content for vectorization
        non_empty_docs = [doc for doc in documents_nouns_only if doc.strip()]
        if len(non_empty_docs) < 2:
            logger.warning("Not enough documents with content for topic modeling, returning basic tags")
            # Return simple word-based tags as fallback
            words = total_content.split()
            unique_words = list(set(words))
            return unique_words[:10]  # Return up to 10 most basic tags
        
        try:
            vectorizer = CountVectorizer(
                stop_words="english",  # Remove common English stop words, should have this use detected language later
                max_features=20000,  # Limit vocabulary size
                binary=True,  # Use binary counts (presence/absence)
                min_df=1,  # Reduced from 2 - word must appear in at least 1 document
                max_df=0.8,  # Word can't appear in more than 80% of documents
                token_pattern=r"\b[a-zA-Z]{3,}\b",  # Only words with 3+ letters
            )

            doc_word = vectorizer.fit_transform(documents_nouns_only)
            doc_word = ss.csr_matrix(doc_word)

            logger.debug(
                "Document-term matrix shape: %s", doc_word.shape
            )  # n_docs x m_words

            # Get words that label the columns (needed to extract readable topics and make anchoring easier)
            words = list(np.asarray(vectorizer.get_feature_names_out()))
            logger.debug("Total vocabulary size (nouns): %d", len(words))
            logger.debug("Sample nouns in vocabulary: %s", words[:20])

            # Count noun frequency across all documents to see most common nouns
            logger.debug("Most common nouns across all documents:")
            all_nouns_text = " ".join(documents_nouns_only)
            noun_counts = Counter(all_nouns_text.split())
            for noun, count in noun_counts.most_common(15):
                if len(noun) >= 3:  # Only show substantial words
                    logger.debug("  %s: %d occurrences", noun, count)

            not_digit_inds = [ind for ind, word in enumerate(words) if not word.isdigit()]
            doc_word = doc_word[:, not_digit_inds]
            words = [word for word in words if not word.isdigit()]

            logger.debug("Document-term matrix shape after filtering: %s", doc_word.shape)
            
            # Check if we still have enough vocabulary
            if len(words) < 5:
                logger.warning("Vocabulary too small for topic modeling, returning simple word tags")
                return words
            
            logger.debug("Training topic model...")
            topic_model = ct.Corex(
                n_hidden=min(10, len(words) // 2),  # Adjust number of topics based on vocabulary size
                words=words, 
                max_iter=200, 
                verbose=False, 
                seed=1
            )
            topic_model.fit(doc_word, words=words)
            logger.debug(
                "Topic model results: %s", topic_model.get_topics(topic=1, n_words=10)
            )

            # Extract all topic words as tags
            tags = []
            topics = topic_model.get_topics()
            for n, topic in enumerate(topics):
                if len(topic) > 0:  # Check if topic has words
                    topic_words, _, _ = zip(*topic)
                    tags.extend(topic_words)
                    logger.debug("Topic %d: %s", n, ", ".join(topic_words))
                else:
                    logger.debug("Topic %d: (empty topic)", n)
            
            # Remove duplicates and return unique tags
            unique_tags = list(set(tags))
            logger.info("Generated %d unique tags from %d topics", len(unique_tags), len(topics))
            return unique_tags
            
        except Exception as e:
            logger.error("Error in topic modeling: %s, falling back to simple word extraction", str(e))
            # Fallback: return most common words as tags
            all_nouns_text = " ".join(documents_nouns_only)
            noun_counts = Counter(all_nouns_text.split())
            common_words = [word for word, count in noun_counts.most_common(20) if len(word) >= 3]
            return common_words

    def tag_content(self, state):
        """
        Workflow node function that adds tags to the setup state
        
        Args:
            state: SetupState containing text to tag
            
        Returns:
            Updated state with tags added
        """
        # Check if we have chapters to process
        if not state.get("all_chapters"):
            logger.warning("No chapters provided for tagging")
            state["tags"] = []
            return state
        
        # Use the tag_text method which expects the full state
        tags = self.tag_text(state)
        state["tags"] = tags
        logger.info("Added %d tags to setup state", len(tags))
        return state

    def _extract_nouns_from_text(self, text: str, max_length=15) -> str:
        """
        Extract only nouns from text using spaCy POS tagging

        Args:
            text: Input text string
            max_length: Maximum word length to include

        Returns:
            String of space-separated nouns
        """
        # Get the spaCy model from the provider
        nlp = self.nlp_provider.get_model("en_core_web_sm")
        
        # Process text with spaCy
        doc = nlp(text)

        # Extract nouns (NOUN and PROPN tags)
        nouns = []
        for token in doc:
            if (
                token.pos_ in ["NOUN", "PROPN"]  # Only nouns and proper nouns
                and not token.is_stop  # Skip stop words
                and not token.is_punct  # Skip punctuation
                and not token.is_space  # Skip whitespace
                and token.is_alpha  # Only alphabetic characters
                and len(token.lemma_) <= max_length
            ):  # Length filter
                # Use lemma (root form) to normalize plurals etc.
                nouns.append(token.lemma_.lower())

        return " ".join(nouns)
