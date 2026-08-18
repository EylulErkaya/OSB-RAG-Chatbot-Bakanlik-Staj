import ollama


MODEL = "nomic-embed-text:v1.5"

text = """
OSB: Malatya OSB
İl: Malatya
Bölge: Doğu Anadolu

Parsel Bilgileri:
- Boş parsel sayısı: 172
- Boş parsel alanı: 434.67 Ha
"""


response = ollama.embed(
    model=MODEL,
    input=text
)

embedding = response["embeddings"][0]

print("=" * 60)
print("OLLAMA EMBEDDING TESTİ")
print("=" * 60)

print(f"Model: {MODEL}")
print(f"Embedding boyutu: {len(embedding)}")

print("\nİlk 10 değer:")
print(embedding[:10])

print("\nTest başarılı.")