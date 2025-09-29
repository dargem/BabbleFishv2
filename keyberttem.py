from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

kw_model = KeyBERT(model)

with open("data/raw/lotm_files/lotm2.txt") as f:
    text = f.read()
text = text.replace("Zhou Mingrui", "<PROTAGONIST>")
tags = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), top_n=10)

print([tag[0].title() for tag in tags])
