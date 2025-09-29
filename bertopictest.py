from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# Example corpus
docs = [
    "The football team won the championship game last night.",
    "Elections are coming up and the candidates are debating healthcare.",
    "I just finished reading a beautiful romance novel.",
    "The basketball league is starting its season.",
    "Parliament passed a new bill on education reform.",
    "Two characters fall in love in this new movie.",
]

# Define seed topics with guiding words
seed_topic_list = [
    ["football", "basketball", "sports", "game", "league"],  # Sports theme
    ["election", "parliament", "politics", "government"],  # Politics theme
    ["romance", "love", "relationship", "novel", "movie"],  # Romance theme
]

# Embedding model (fast + small)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Build BERTopic model with seed guidance
topic_model = BERTopic(
    embedding_model=embedding_model, seed_topic_list=seed_topic_list, verbose=True
)

topics, probs = topic_model.fit_transform(docs)

# Inspect results
print("\nAssigned topics:", topics)
print("\nTopic labels:")
print(topic_model.get_topic_info())
