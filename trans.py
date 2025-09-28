from transformers import pipeline

classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")


with open("data/raw/lotm_files/lotm2.txt") as f:
    text = f.read()

tags = [
    "transmigration",
    "supernatural healing",
    "fear",
    "horror",
    "memory fragments",
    "poverty",
    "family struggles",
    "gas lamps",
    "old technology",
    "mystery",
    "detective elements",
    "suicide",
    "revolver",
    "ritual",
    "divination",
    "crimson moon",
    "eerie atmosphere",
    "space travel",
    "modern smartphones",
    "artificial intelligence",
    "corporate finance",
    "ocean exploration",
    "cooking recipes",
    "science experiments",
    "romance comedy",
    "sports",
    "futuristic technology"
]


print("starting")
result = classifier(text, tags)

print(result)

for i in range(len(result['scores'])-1):
    print("-----tag------")
    print(result['labels'][i])
    print(result['scores'][i])
