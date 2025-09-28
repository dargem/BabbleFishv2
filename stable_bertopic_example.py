"""
Fixed BERTopic example that avoids segmentation faults
"""
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import os
import warnings

# Suppress warnings and set environment variables to prevent crashes
warnings.filterwarnings("ignore")
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1" 
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Example corpus (larger dataset to avoid UMAP issues)
docs = [
    "The football team won the championship game last night.",
    "Elections are coming up and the candidates are debating healthcare.",
    "I just finished reading a beautiful romance novel.",
    "The basketball league is starting its season.",
    "Parliament passed a new bill on education reform.",
    "Two characters fall in love in this new movie.",
    "Soccer players are training for the world cup.",
    "The government announced new policies today.",
    "This romantic comedy made me cry happy tears.",
    "Tennis tournament begins next week.",
    "Political parties are forming coalitions.",
    "The love story between the main characters was touching.",
    "Baseball season is almost over.",
    "Voters will decide on the referendum.",
    "The romantic dinner scene was beautifully filmed.",
    "Hockey playoffs start tomorrow.",
    "Congressional hearings on climate change.",
    "Their wedding was the perfect ending to the romance.",
]

print(f"Processing {len(docs)} documents...")

# Use simpler, more stable components
print("Setting up embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Configuring BERTopic with stable components...")

# Use PCA instead of UMAP to avoid crashes
from sklearn.decomposition import PCA
pca_model = PCA(n_components=2, random_state=42)

# Use KMeans clustering instead of HDBSCAN for stability
from sklearn.cluster import KMeans
kmeans_model = KMeans(n_clusters=3, random_state=42, n_init=10)

# Create BERTopic model with stable components
topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=pca_model,  # Use PCA instead of UMAP
    hdbscan_model=kmeans_model,  # Use KMeans instead of HDBSCAN
    verbose=True,
    calculate_probabilities=False,  # Disable probabilities to avoid memory issues
    nr_topics="auto"
)

print("Fitting the model...")
try:
    topics, probs = topic_model.fit_transform(docs)
    
    print(f"\n✅ Success! Model fitted without crashes.")
    print(f"Found {len(set(topics))} topics")
    print(f"Assigned topics: {topics}")
    
    # Get topic information
    topic_info = topic_model.get_topic_info()
    print(f"\nTopic Information:")
    print(topic_info)
    
    # Show top words for each topic
    print(f"\nTop words per topic:")
    for topic_id in topic_info['Topic']:
        if topic_id != -1:  # Skip outlier topic
            words = topic_model.get_topic(topic_id)[:5]  # Top 5 words
            word_list = [word for word, score in words]
            print(f"Topic {topic_id}: {', '.join(word_list)}")
            
    # Show which documents belong to which topic
    print(f"\nDocument-Topic assignments:")
    for i, (doc, topic) in enumerate(zip(docs, topics)):
        print(f"Doc {i}: Topic {topic} - '{doc[:50]}...'")
        
except Exception as e:
    print(f"❌ Error occurred: {e}")
    print("This might be due to the dataset being too small or dependency conflicts.")
    
    # Alternative: Use a simpler approach
    print("\nTrying alternative clustering approach...")
    
    # Just do basic clustering without BERTopic
    embeddings = embedding_model.encode(docs)
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(embeddings)
    
    print("Simple clustering results:")
    for i, (doc, cluster) in enumerate(zip(docs, clusters)):
        print(f"Doc {i}: Cluster {cluster} - '{doc[:50]}...'")

print("\n🎉 Script completed without segmentation fault!")