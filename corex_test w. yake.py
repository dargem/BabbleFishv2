import numpy as np
import scipy.sparse as ss
import matplotlib.pyplot as plt
import os
import corextopic.corextopic as ct
import corextopic.vis_topic as vt  # jupyter notebooks will complain matplotlib is being loaded twice
import spacy
from collections import Counter

from sklearn.feature_extraction.text import CountVectorizer


# Load spaCy model for noun extraction
print("Loading spaCy model for noun extraction...")
nlp = spacy.load("en_core_web_sm")


def extract_nouns_from_text(text, min_length=3, max_length=15):
    """
    Extract only nouns from text using spaCy POS tagging

    Args:
        text: Input text string
        min_length: Minimum word length to include
        max_length: Maximum word length to include

    Returns:
        String of space-separated nouns
    """
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
            and min_length <= len(token.lemma_) <= max_length
        ):  # Length filter
            # Use lemma (root form) to normalize plurals etc.
            nouns.append(token.lemma_.lower())

    return " ".join(nouns)


data_dir = "data/raw/lotm_files_extended/"

# Create a list to hold the content of each document
documents = []
documents_nouns_only = []

# Loop through each file in the specified directory
for filename in os.listdir(data_dir):
    print(f"Processing: {filename}")
    # Make sure we're only reading .txt files
    if filename.endswith(".txt"):
        # Construct the full file path
        filepath = os.path.join(data_dir, filename)
        # Open and read the file, then add its content to our list
        with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
            original_text = file.read()
            documents.append(original_text)

            # Extract only nouns from the text
            print(f"  Extracting nouns from {filename}...")
            nouns_only = extract_nouns_from_text(original_text)
            documents_nouns_only.append(nouns_only)
            print(f"  Original length: {len(original_text)} chars")
            print(f"  Nouns only length: {len(nouns_only)} chars")
            print(f"  Sample nouns: {nouns_only[:100]}...")

print(f"\nProcessed {len(documents)} documents")
print(f"Using noun-only versions for topic modeling...")

# Transform noun-only documents into a sparse matrix
print("\nCreating document-term matrix from nouns...")
vectorizer = CountVectorizer(
    stop_words="english",  # Remove common English stop words
    max_features=20000,  # Limit vocabulary size
    binary=True,  # Use binary counts (presence/absence)
    min_df=2,  # Word must appear in at least 2 documents
    max_df=0.8,  # Word can't appear in more than 80% of documents
    token_pattern=r"\b[a-zA-Z]{3,}\b",  # Only words with 3+ letters
)
doc_word = vectorizer.fit_transform(documents_nouns_only)
doc_word = ss.csr_matrix(doc_word)

print(f"Document-term matrix shape: {doc_word.shape}")  # n_docs x m_words

# Get words that label the columns (needed to extract readable topics and make anchoring easier)
words = list(np.asarray(vectorizer.get_feature_names_out()))
print(f"Total vocabulary size (nouns): {len(words)}")
print(f"Sample nouns in vocabulary: {words[:20]}")

# Count noun frequency across all documents to see most common nouns
print(f"\nMost common nouns across all documents:")
all_nouns_text = " ".join(documents_nouns_only)
noun_counts = Counter(all_nouns_text.split())
for noun, count in noun_counts.most_common(15):
    if len(noun) >= 3:  # Only show substantial words
        print(f"  {noun}: {count} occurrences")

not_digit_inds = [ind for ind, word in enumerate(words) if not word.isdigit()]
doc_word = doc_word[:, not_digit_inds]
words = [word for ind, word in enumerate(words) if not word.isdigit()]

print(doc_word.shape)  # n_docs x m_words

# Train the CorEx topic model with 50 topics
topic_model = ct.Corex(n_hidden=50, words=words, max_iter=200, verbose=False, seed=1)
topic_model.fit(doc_word, words=words)
print(topic_model.get_topics(topic=1, n_words=10))

# Print all topics from the CorEx topic model
text = ""
topics = topic_model.get_topics()
for n, topic in enumerate(topics):
    if len(topic) > 0:  # Check if topic has words
        topic_words, _, _ = zip(*topic)
        for word in topic_words:
            text += word + " "
        print("{}: ".format(n) + ", ".join(topic_words))
    else:
        print("{}: (empty topic)".format(n))


import yake

# With custom parameters
custom_kw_extractor = yake.KeywordExtractor(
    lan="en",  # language
    n=1,  # ngram size
    dedupLim=0.9,  # deduplication threshold
    dedupFunc="seqm",  # deduplication function
    windowsSize=1,  # context window
    top=10,  # number of keywords to extract
    features=None,  # custom features
)

keywords = custom_kw_extractor.extract_keywords(text)
print("custom")
for kw, score in keywords:
    print(f"{kw} ({score})")
