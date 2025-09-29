"""
Enhanced preprocessing pipeline for CorEx topic modeling
"""

import numpy as np
import spacy
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords


class EnhancedTextProcessor:
    def __init__(self, language="en"):
        self.nlp = spacy.load("en_core_web_sm")
        # Add custom stop words specific to your domain
        self.custom_stop_words = {
            "chapter",
            "translator",
            "editor",
            "atlasstudios",
            "said",
            "say",
            "go",
            "come",
            "take",
            "make",
            "get",
        }

    def extract_enhanced_nouns(self, text, min_length=3, max_length=20):
        """Enhanced noun extraction with better filtering"""
        doc = self.nlp(text)
        nouns = []

        for token in doc:
            if (
                token.pos_ in ["NOUN", "PROPN"]
                and not token.is_stop
                and not token.is_punct
                and not token.is_space
                and token.is_alpha
                and min_length <= len(token.lemma_) <= max_length
                and token.lemma_.lower() not in self.custom_stop_words
                and not token.like_num  # Remove number-like tokens
                and not token.is_currency
            ):  # Remove currency symbols
                lemma = token.lemma_.lower()
                # Filter out very common/generic words that add no meaning
                if not self._is_generic_word(lemma):
                    nouns.append(lemma)

        return " ".join(nouns)

    def _is_generic_word(self, word):
        """Filter out overly generic words"""
        generic_words = {
            "thing",
            "way",
            "time",
            "day",
            "year",
            "place",
            "part",
            "world",
            "life",
            "work",
            "case",
            "point",
            "fact",
            "side",
        }
        return word in generic_words

    def extract_named_entities(self, text):
        """Extract named entities (characters, locations, organizations)"""
        doc = self.nlp(text)
        entities = {}

        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "LOC"]:
                entity_text = ent.text.lower().strip()
                if len(entity_text) > 2:
                    entities[entity_text] = ent.label_

        return entities

    def get_noun_phrases(self, text, min_words=2, max_words=4):
        """Extract meaningful noun phrases"""
        doc = self.nlp(text)
        phrases = []

        for chunk in doc.noun_chunks:
            # Clean the chunk
            chunk_text = " ".join(
                [
                    token.lemma_.lower()
                    for token in chunk
                    if not token.is_stop and token.is_alpha
                ]
            )

            word_count = len(chunk_text.split())
            if min_words <= word_count <= max_words and len(chunk_text) > 5:
                phrases.append(chunk_text)

        return phrases


# Usage example:
processor = EnhancedTextProcessor()


def improved_preprocessing_pipeline(documents):
    """
    Improved preprocessing pipeline
    """
    processed_docs = []
    all_entities = {}
    all_phrases = []

    for i, doc in enumerate(documents):
        print(f"Processing document {i + 1}/{len(documents)}...")

        # 1. Extract enhanced nouns
        nouns = processor.extract_enhanced_nouns(doc)

        # 2. Extract named entities
        entities = processor.extract_named_entities(doc)
        all_entities.update(entities)

        # 3. Extract noun phrases
        phrases = processor.get_noun_phrases(doc)
        all_phrases.extend(phrases)

        # 4. Combine nouns and important entities
        entity_names = " ".join(
            [
                ent
                for ent in entities.keys()
                if entities[ent] in ["PERSON", "ORG", "GPE"]
            ]
        )

        combined_text = f"{nouns} {entity_names}"
        processed_docs.append(combined_text)

    return processed_docs, all_entities, all_phrases


# Example usage in your pipeline:
# processed_docs, entities, phrases = improved_preprocessing_pipeline(documents)
