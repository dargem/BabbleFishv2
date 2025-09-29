"""
Enhanced post-processing and visualization for CorEx results
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity


class CorexAnalyzer:
    def __init__(self, model, documents, vectorizer):
        self.model = model
        self.documents = documents
        self.vectorizer = vectorizer

    def create_topic_wordclouds(self, save_path="topic_wordclouds"):
        """Create word clouds for each topic"""
        topics = self.model.get_topics()

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for i, topic in enumerate(topics[:6]):  # Show first 6 topics
            if len(topic) > 0:
                # Create word frequency dictionary
                word_freq = {
                    word: float(corr) for word, corr, _ in topic[:20] if corr > 0
                }

                if word_freq:
                    wordcloud = WordCloud(
                        width=400,
                        height=300,
                        background_color="white",
                        colormap="viridis",
                    ).generate_from_frequencies(word_freq)

                    axes[i].imshow(wordcloud, interpolation="bilinear")
                    axes[i].set_title(f"Topic {i}")
                    axes[i].axis("off")

        plt.tight_layout()
        plt.savefig(f"{save_path}.png", dpi=300, bbox_inches="tight")
        plt.show()

    def create_topic_network(self, similarity_threshold=0.3):
        """Create network graph showing topic relationships"""
        topics = self.model.get_topics()

        # Create topic similarity matrix
        topic_vectors = []
        topic_labels = []

        for i, topic in enumerate(topics):
            if len(topic) > 5:  # Only topics with enough words
                # Create vector from top words
                word_scores = {word: float(corr) for word, corr, _ in topic[:10]}
                topic_vectors.append(list(word_scores.values()))

                # Create label from top 3 words
                top_words = [word for word, _, _ in topic[:3]]
                topic_labels.append(f"T{i}: {', '.join(top_words)}")

        if len(topic_vectors) > 1:
            # Calculate similarities
            similarity_matrix = cosine_similarity(topic_vectors)

            # Create network graph
            G = nx.Graph()

            # Add nodes
            for i, label in enumerate(topic_labels):
                G.add_node(i, label=label)

            # Add edges for similar topics
            for i in range(len(similarity_matrix)):
                for j in range(i + 1, len(similarity_matrix)):
                    similarity = similarity_matrix[i][j]
                    if similarity > similarity_threshold:
                        G.add_edge(i, j, weight=similarity)

            # Plot network
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G, k=3, iterations=50)

            # Draw nodes
            nx.draw_nodes(G, pos, node_color="lightblue", node_size=1000, alpha=0.7)

            # Draw edges with thickness based on similarity
            edges = G.edges()
            weights = [G[u][v]["weight"] for u, v in edges]
            nx.draw_edges(
                G, pos, width=[w * 5 for w in weights], alpha=0.6, edge_color="gray"
            )

            # Add labels
            labels = nx.get_node_attributes(G, "label")
            nx.draw_networkx_labels(G, pos, labels, font_size=8)

            plt.title("Topic Similarity Network")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig("topic_network.png", dpi=300, bbox_inches="tight")
            plt.show()

    def analyze_document_topics(self, top_n=5):
        """Analyze which topics are most prominent in each document"""
        doc_word = self.vectorizer.transform(self.documents)
        doc_topic_probs = self.model.transform(doc_word)

        results = []

        for i, doc in enumerate(self.documents):
            # Get top topics for this document
            top_topic_indices = np.argsort(doc_topic_probs[i])[-top_n:][::-1]

            doc_info = {
                "document_id": i,
                "document_preview": doc[:100] + "...",
                "top_topics": [],
            }

            for topic_idx in top_topic_indices:
                prob = doc_topic_probs[i][topic_idx]
                if prob > 0.05:  # Only show topics with >5% probability
                    # Get topic words
                    topic = self.model.get_topics()[topic_idx]
                    if len(topic) > 0:
                        top_words = [word for word, _, _ in topic[:3]]
                        doc_info["top_topics"].append(
                            {
                                "topic_id": topic_idx,
                                "probability": prob,
                                "top_words": top_words,
                            }
                        )

            results.append(doc_info)

        return results

    def create_topic_evolution_chart(self):
        """Show how topics evolve across documents (assuming chronological order)"""
        doc_word = self.vectorizer.transform(self.documents)
        doc_topic_probs = self.model.transform(doc_word)

        # Create DataFrame for easier plotting
        df = pd.DataFrame(
            doc_topic_probs,
            columns=[f"Topic {i}" for i in range(doc_topic_probs.shape[1])],
        )

        # Plot topic evolution
        plt.figure(figsize=(14, 8))

        # Select top topics (those with highest average probability)
        topic_means = df.mean()
        top_topics = topic_means.nlargest(8).index

        for topic in top_topics:
            plt.plot(df.index, df[topic], label=topic, marker="o", linewidth=2)

        plt.xlabel("Document Index")
        plt.ylabel("Topic Probability")
        plt.title("Topic Evolution Across Documents")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("topic_evolution.png", dpi=300, bbox_inches="tight")
        plt.show()

    def generate_topic_summary_report(self):
        """Generate comprehensive report of topic analysis"""
        topics = self.model.get_topics()
        doc_word = self.vectorizer.transform(self.documents)
        doc_topic_probs = self.model.transform(doc_word)

        print("\n" + "=" * 80)
        print("COMPREHENSIVE TOPIC ANALYSIS REPORT")
        print("=" * 80)

        print(f"Model Configuration:")
        print(f"  - Number of topics: {len(topics)}")
        print(f"  - Number of documents: {len(self.documents)}")
        print(f"  - Vocabulary size: {len(self.vectorizer.get_feature_names_out())}")
        print(f"  - Total correlation: {self.model.tc:.4f}")

        print(f"\nTopic Quality Metrics:")

        # Topic coverage
        active_topics = np.sum(doc_topic_probs > 0.1, axis=0)
        print(f"  - Average documents per topic: {np.mean(active_topics):.1f}")
        print(
            f"  - Topics with >50% document coverage: {np.sum(active_topics > len(self.documents) * 0.5)}"
        )

        # Topic specificity
        topic_specificities = []
        for i, topic in enumerate(topics):
            if len(topic) > 0:
                correlations = [corr for _, corr, _ in topic[:10]]
                specificity = np.mean(correlations)
                topic_specificities.append(specificity)

        if topic_specificities:
            print(f"  - Average topic specificity: {np.mean(topic_specificities):.4f}")
            print(f"  - Most specific topic: {np.max(topic_specificities):.4f}")

        print(f"\nTop 10 Most Prominent Topics:")
        topic_prominence = np.mean(doc_topic_probs, axis=0)
        top_topic_indices = np.argsort(topic_prominence)[-10:][::-1]

        for rank, topic_idx in enumerate(top_topic_indices, 1):
            if topic_idx < len(topics) and len(topics[topic_idx]) > 0:
                topic = topics[topic_idx]
                top_words = [word for word, _, _ in topic[:5]]
                prominence = topic_prominence[topic_idx]
                print(
                    f"  {rank:2d}. Topic {topic_idx}: {', '.join(top_words)} "
                    f"(prominence: {prominence:.3f})"
                )


# Usage example:
# analyzer = CorexAnalyzer(topic_model, documents_nouns_only, vectorizer)
# analyzer.create_topic_wordclouds()
# analyzer.create_topic_network()
# doc_analysis = analyzer.analyze_document_topics()
# analyzer.generate_topic_summary_report()
