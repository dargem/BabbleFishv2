"""
Improved vectorization strategies for CorEx
"""

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline
import numpy as np


class ImprovedVectorizer:
    def __init__(self, method="hybrid"):
        self.method = method

    def create_vectorizer(self, documents, max_features=5000):
        """Create optimized vectorizer based on your data"""

        if self.method == "tfidf":
            # TF-IDF often works better than binary for topic modeling
            return TfidfVectorizer(
                stop_words="english",
                max_features=max_features,
                min_df=3,  # Word must appear in at least 3 documents
                max_df=0.7,  # Word can't be in more than 70% of docs
                ngram_range=(1, 2),  # Include bigrams for context
                sublinear_tf=True,  # Apply sublinear tf scaling
                norm="l2",  # L2 normalization
            )

        elif self.method == "hybrid":
            # Combination approach: use both unigrams and bigrams
            return TfidfVectorizer(
                stop_words="english",
                max_features=max_features,
                min_df=2,
                max_df=0.8,
                ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
                token_pattern=r"\b[a-zA-Z][a-zA-Z]+\b",  # At least 2 chars
                lowercase=True,
                strip_accents="unicode",
            )

        else:  # count_based (your current method)
            return CountVectorizer(
                stop_words="english",
                max_features=max_features,
                binary=True,
                min_df=2,
                max_df=0.8,
                token_pattern=r"\b[a-zA-Z]{3,}\b",
            )


def adaptive_feature_selection(doc_word_matrix, words, top_k=1000):
    """
    Select most informative features using SVD
    """
    # Use SVD to find most important dimensions
    svd = TruncatedSVD(n_components=min(50, doc_word_matrix.shape[1] - 1))
    svd.fit(doc_word_matrix)

    # Get feature importance scores
    feature_scores = np.sum(np.abs(svd.components_), axis=0)

    # Select top features
    top_indices = np.argsort(feature_scores)[-top_k:]
    selected_words = [words[i] for i in top_indices]
    selected_matrix = doc_word_matrix[:, top_indices]

    return selected_matrix, selected_words


# Example usage:
# vectorizer = ImprovedVectorizer(method='hybrid')
# vec = vectorizer.create_vectorizer(documents_nouns_only)
# doc_word = vec.fit_transform(documents_nouns_only)
