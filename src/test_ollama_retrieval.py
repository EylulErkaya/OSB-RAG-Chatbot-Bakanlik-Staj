import json
import math
import ollama


MODEL = "nomic-embed-text:v1.5"
CHUNKS_PATH = "data/documents/chunks.jsonl"


# --------------------------------------------------
# CHUNK'LARI OKU
# --------------------------------------------------

chunks = []

with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            chunks.append(json.loads(line))


print("=" * 70)
print("OLLAMA RETRIEVAL TESTİ")
print("=" * 70)

print(f"Toplam chunk: {len(chunks)}")


# --------------------------------------------------
# TEST İÇİN KÜÇÜK ÖRNEK
# --------------------------------------------------

# İlk aşamada bütün 13.514 chunk'ı embed etmiyoruz.
# Test için ilk 200 chunk yeterli.

test_chunks = chunks[:200]

print(f"Test edilen chunk: {len(test_chunks)}")


# --------------------------------------------------
# EMBEDDING
# --------------------------------------------------

print("\nChunk embeddingleri oluşturuluyor...")

chunk_embeddings = []

for i, chunk in enumerate(test_chunks, start=1):

    response = ollama.embed(
        model=MODEL,
        input=chunk["text"]
    )

    embedding = response["embeddings"][0]

    chunk_embeddings.append(embedding)

    if i % 25 == 0:
        print(f"{i}/{len(test_chunks)}")


print("Embedding işlemi tamamlandı.")


# --------------------------------------------------
# COSINE SIMILARITY
# --------------------------------------------------

def cosine_similarity(a, b):

    dot_product = sum(
        x * y
        for x, y in zip(a, b)
    )

    norm_a = math.sqrt(
        sum(x * x for x in a)
    )

    norm_b = math.sqrt(
        sum(y * y for y in b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0

    return dot_product / (
        norm_a * norm_b
    )


# --------------------------------------------------
# ARAMA
# --------------------------------------------------

def search(query, top_k=5):

    response = ollama.embed(
        model=MODEL,
        input=query
    )

    query_embedding = response["embeddings"][0]

    results = []

    for chunk, embedding in zip(
        test_chunks,
        chunk_embeddings
    ):

        score = cosine_similarity(
            query_embedding,
            embedding
        )

        results.append({
            "score": score,
            "chunk": chunk
        })


    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:top_k]


# --------------------------------------------------
# TEST SORULARI
# --------------------------------------------------

queries = [
    "Malatya OSB'de kaç boş parsel var?",
    "Malatya OSB hangi bölgede bulunuyor?",
    "Malatya OSB'de kaç kişi istihdam ediliyor?",
    "Malatya OSB'de gıda sektöründe kaç kişi çalışıyor?",
    "Malatya OSB'de kaç fabrika üretim yapıyor?",
]


# --------------------------------------------------
# TEST
# --------------------------------------------------

print("\n" + "=" * 70)
print("SORU - RETRIEVAL TESTLERİ")
print("=" * 70)


for query in queries:

    print("\n" + "-" * 70)
    print(f"SORU: {query}")
    print("-" * 70)

    results = search(
        query,
        top_k=5
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        chunk = result["chunk"]

        print(
            f"\n#{rank} "
            f"Score: {result['score']:.4f}"
        )

        print(
            f"ID: {chunk['chunk_id']}"
        )

        print(
            f"Tip: "
            f"{chunk['metadata']['chunk_type']}"
        )

        print(
            chunk["text"][:300]
        )


print("\n" + "=" * 70)
print("RETRIEVAL TESTİ TAMAMLANDI")
print("=" * 70)