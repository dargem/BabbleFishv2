from enhanced_preprocessing import EnhancedTextProcessor
from improved_vectorization import ImprovedVectorizer
from optimized_corex import OptimizedCorexModel
from corex_analysis import CorexAnalyzer
import os

data_dir = "data/raw/lotm_files_extended/"
documents = []
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

processor = EnhancedTextProcessor()
processed_docs, entities, phrases = processor.improved_preprocessing_pipeline(documents)

# 2. Better vectorization
vectorizer = ImprovedVectorizer(method="hybrid")
vec = vectorizer.create_vectorizer(processed_docs)
doc_word = vec.fit_transform(processed_docs)

# 3. Optimize topic model
optimizer = OptimizedCorexModel()
best_n_topics, best_model = optimizer.find_optimal_topics(
    doc_word, vec.get_feature_names_out()
)

# 4. Comprehensive analysis
analyzer = CorexAnalyzer(best_model, processed_docs, vec)
analyzer.generate_topic_summary_report()
analyzer.create_topic_wordclouds()
