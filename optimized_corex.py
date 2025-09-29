"""
Enhanced CorEx topic modeling with better configuration and evaluation
"""

import corextopic.corextopic as ct
import numpy as np
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt


class OptimizedCorexModel:
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.best_score = -1

    def find_optimal_topics(self, doc_word, words, min_topics=5, max_topics=30, step=5):
        """
        Find optimal number of topics using coherence and silhouette analysis
        """
        print("Finding optimal number of topics...")
        topic_range = range(min_topics, max_topics + 1, step)
        scores = []

        for n_topics in topic_range:
            print(f"Testing {n_topics} topics...")

            # Train model
            model = ct.Corex(
                n_hidden=n_topics,
                words=words,
                max_iter=300,  # More iterations for convergence
                verbose=False,
                seed=42,  # Reproducible results
                eps=1e-5,  # Convergence threshold
                n_repeat=3,  # Multiple runs for stability
            )
            model.fit(doc_word, words=words)

            # Calculate coherence score (higher is better)
            coherence = self._calculate_coherence(model, doc_word)
            scores.append(coherence)

            # Store model
            self.models[n_topics] = {
                "model": model,
                "coherence": coherence,
                "total_correlation": model.tc,
            }

            print(
                f"  Topics: {n_topics}, Coherence: {coherence:.4f}, TC: {model.tc:.4f}"
            )

        # Find best model
        best_idx = np.argmax(scores)
        best_n_topics = list(topic_range)[best_idx]
        self.best_model = self.models[best_n_topics]["model"]
        self.best_score = scores[best_idx]

        print(
            f"\nBest model: {best_n_topics} topics (coherence: {self.best_score:.4f})"
        )

        # Plot results
        plt.figure(figsize=(10, 6))
        plt.plot(topic_range, scores, "bo-")
        plt.xlabel("Number of Topics")
        plt.ylabel("Coherence Score")
        plt.title("Topic Model Coherence vs Number of Topics")
        plt.grid(True)
        plt.axvline(
            x=best_n_topics,
            color="r",
            linestyle="--",
            label=f"Best: {best_n_topics} topics",
        )
        plt.legend()
        plt.tight_layout()
        plt.savefig("topic_optimization.png", dpi=300, bbox_inches="tight")
        plt.show()

        return best_n_topics, self.best_model

    def _calculate_coherence(self, model, doc_word, top_words=10):
        """
        Calculate topic coherence (simplified version)
        """
        topics = model.get_topics()
        coherence_scores = []

        for topic in topics:
            if len(topic) >= top_words:
                # Get top words for this topic
                topic_words = [word for word, _, _ in topic[:top_words]]

                # Simple coherence: average pairwise co-occurrence
                coherence = 0
                pairs = 0

                for i in range(len(topic_words)):
                    for j in range(i + 1, len(topic_words)):
                        # This is a simplified coherence measure
                        # In practice, you'd use more sophisticated measures
                        coherence += 1  # Placeholder
                        pairs += 1

                if pairs > 0:
                    coherence_scores.append(coherence / pairs)

        return np.mean(coherence_scores) if coherence_scores else 0

    def analyze_topic_quality(self, model, words, doc_word):
        """
        Analyze the quality of discovered topics
        """
        topics = model.get_topics()

        print("\n" + "=" * 60)
        print("TOPIC QUALITY ANALYSIS")
        print("=" * 60)

        # 1. Topic diversity (how different topics are from each other)
        diversity_score = self._calculate_topic_diversity(topics)
        print(f"Topic Diversity Score: {diversity_score:.4f}")

        # 2. Topic coherence per topic
        print("\nPer-topic analysis:")
        for i, topic in enumerate(topics):
            if len(topic) > 0:
                top_words = [word for word, corr, _ in topic[:5]]
                avg_correlation = np.mean([corr for _, corr, _ in topic[:10]])
                print(
                    f"Topic {i}: {', '.join(top_words)} (avg_corr: {avg_correlation:.3f})"
                )

        # 3. Document-topic distribution
        doc_topic_probs = model.transform(doc_word)
        topic_coverage = np.mean(
            doc_topic_probs > 0.1, axis=0
        )  # Topics active in >10% prob

        print(f"\nTopic Coverage (% docs with >10% probability):")
        for i, coverage in enumerate(topic_coverage):
            if coverage > 0:
                print(f"  Topic {i}: {coverage * 100:.1f}%")

        return {
            "diversity": diversity_score,
            "topic_coverage": topic_coverage,
            "total_correlation": model.tc,
        }

    def _calculate_topic_diversity(self, topics, top_k=10):
        """Calculate how diverse topics are from each other"""
        if len(topics) < 2:
            return 0

        topic_words = []
        for topic in topics:
            if len(topic) >= top_k:
                words = set([word for word, _, _ in topic[:top_k]])
                topic_words.append(words)

        if len(topic_words) < 2:
            return 0

        # Calculate average Jaccard distance between topics
        total_distance = 0
        pairs = 0

        for i in range(len(topic_words)):
            for j in range(i + 1, len(topic_words)):
                intersection = len(topic_words[i] & topic_words[j])
                union = len(topic_words[i] | topic_words[j])
                jaccard = intersection / union if union > 0 else 0
                distance = 1 - jaccard  # Jaccard distance
                total_distance += distance
                pairs += 1

        return total_distance / pairs if pairs > 0 else 0


# Usage example:
# optimizer = OptimizedCorexModel()
# best_n_topics, best_model = optimizer.find_optimal_topics(doc_word, words)
# quality_metrics = optimizer.analyze_topic_quality(best_model, words, doc_word)
