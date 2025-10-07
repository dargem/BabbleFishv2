"""Creates tags for a novels input"""

import logging
import numpy as np
import scipy.sparse as ss
import matplotlib.pyplot as plt
import corextopic.corextopic as ct
import corextopic.vis_topic as vt  # jupyter notebooks will complain matplotlib is being loaded twice
import spacy
from collections import Counter
from src.providers import LLMProvider
from sklearn.feature_extraction.text import CountVectorizer
from typing import List

logger = logging.getLogger(__name__)


class Tagger:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        logger.debug("Loading spaCy model")
        self.nlp = spacy.load("en_core_web_sm")

    def tag_text(self, chapters: List[str]) -> List[str]:
        """
        Args:
            text: The input text as a list of chapters

        Returns:
            List of tags (strings) from the text
        """

        documents = [self._extract_nouns_from_text(chapter) for chapter in chapters]

        vectorizer = CountVectorizer(
            stop_words="english",  # Remove common English stop words, should have this use detected language later
            max_features=20000,  # Limit vocabulary size
            binary=True,  # Use binary counts (presence/absence)
            min_df=2,  # Word must appear in at least 2 documents
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
        words = [word for word in words.values() if not word.isdigit()]

        logger.debug("Document-term matrix shape: %s", doc_word.shape)

        logger.debug("Training topic model...")
        topic_model = ct.Corex(
            n_hidden=50, words=words, max_iter=200, verbose=False, seed=1
        )
        topic_model.fit(doc_word, words=words)
        logger.debug(
            "Topic model results: %s", topic_model.get_topics(topic=1, n_words=10)
        )

        # Print all topics from the CorEx topic model
        text = ""
        topics = topic_model.get_topics()
        for n, topic in enumerate(topics):
            if len(topic) > 0:  # Check if topic has words
                topic_words, _, _ = zip(*topic)
                for word in topic_words:
                    text += word + " "
                logger.debug("Topic %d: %s", n, ", ".join(topic_words))
            else:
                logger.debug("Topic %d: (empty topic)", n)

    def _extract_nouns_from_text(self, text: str, max_length=15) -> str:
        """
        Extract only nouns from text using spaCy POS tagging

        Args:
            text: Input text string
            max_length: Maximum word length to include

        Returns:
            String of space-separated nouns
        """
        # Process text with spaCy
        doc = self.nlp(text)

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
