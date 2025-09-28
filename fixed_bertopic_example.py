"""
Simple fix for the original BERTopic segmentation fault
"""
import os
import warnings

# CRITICAL: Set these environment variables BEFORE importing any ML libraries
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Suppress the OpenMP warnings
warnings.filterwarnings("ignore")

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# Your original example corpus (extended to avoid small dataset issues)
docs = [
    "The football team won the championship game last night.",
    "Elections are coming up and the candidates are debating healthcare.",
    "I just finished reading a beautiful romance novel.",
    "The basketball league is starting its season.",
    "Parliament passed a new bill on education reform.",
    "Two characters fall in love in this new movie.",
    # Add more similar documents to make dataset larger
    "Soccer match was exciting with great goals scored.",
    "Political debate focused on economic policies tonight.",
    "Romance books always make me feel emotional and happy.",
    "Tennis tournament features top ranked players this year.",
    "Government officials announced infrastructure spending plans today.",
    "Love story movies are perfect for weekend entertainment."
]

# Your original seed topics
seed_topic_list = [
    ["football", "basketball", "sports", "game", "league"],   
    ["election", "parliament", "politics", "government"],     
    ["romance", "love", "relationship", "novel", "movie"],    
]

print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Building BERTopic model...")
# Build with additional stability settings
topic_model = BERTopic(
    embedding_model=embedding_model,
    seed_topic_list=seed_topic_list,
    verbose=True,
    calculate_probabilities=False,  # Disable to reduce memory/crash issues
    low_memory=True,               # Enable low memory mode
)

print("Fitting model...")
topics, probs = topic_model.fit_transform(docs)

# Results
print(f"\n✅ Success! Assigned topics: {topics}")
print(f"\nTopic labels:")
print(topic_model.get_topic_info())

print(f"\nDocument assignments:")
for i, (doc, topic) in enumerate(zip(docs, topics)):
    print(f"Doc {i}: Topic {topic} - '{doc[:40]}...'")