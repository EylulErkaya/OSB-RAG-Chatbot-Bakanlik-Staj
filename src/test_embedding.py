import json
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

MODEL_NAME = "intfloat/multilingual-e5-large-instruct"

CHUNKS_PATH = "data/documents/chunks.jsonl"


# --------------------------------------------------
# MODELİ YÜKLE
# --------------------------------------------------

print("=" * 70)
print("EMBEDDING MODELİ")
print("=" * 70)

print(f"Model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)

print("Model başarıyla yüklendi.")


# --------------------------------------------------
# CHUNK'LARI OKU
# --------------------------------------------------

chunks = []

with open(
    CHUNKS_PATH,
    "r",
    encoding="utf-8"
) as file:

    for line in file:

        if line.strip():
            chunks.append(
                json.loads(line)
            )


print(f"Chunk sayısı: {len(chunks)}")


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
# CHUNK METİNLERİ
# --------------------------------------------------

chunk_texts = [
    chunk["text"]
    for chunk in chunks
]


# --------------------------------------------------
# PASSAGE EMBEDDING
# --------------------------------------------------

print("\nChunk embeddingleri oluşturuluyor...")

chunk_embeddings = model.encode(
    chunk_texts,
    batch_size=16,
    show_progress_bar=True,
    normalize_embeddings=True,
)

print(
    f"Embedding boyutu: "
    f"{chunk_embeddings.shape}"
)


# --------------------------------------------------
# QUERY EMBEDDING
# --------------------------------------------------

def create_query_embedding(query):

    instruction = (
        "Instruct: "
        "Kullanıcının sorusuna cevap vermek için "
        "ilgili OSB veya sektör bilgisini bul.\n"
        f"Query: {query}"
    )

    return model.encode(
        instruction,
        normalize_embeddings=True
    )


# --------------------------------------------------
# COSINE SIMILARITY
# --------------------------------------------------

def search(query, top_k=5):

    query_embedding = create_query_embedding(
        query
    )

    scores = np.dot(
        chunk_embeddings,
        query_embedding
    )

    top_indices = np.argsort(
        scores
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        results.append({
            "score": float(scores[index]),
            "chunk": chunks[index]
        })

    return results


# --------------------------------------------------
# TESTLER
# --------------------------------------------------

print("\n" + "=" * 70)
print("RETRIEVAL TESTLERİ")
print("=" * 70)


for query in queries:

    print("\n" + "-" * 70)
    print(f"SORU: {query}")
    print("-" * 70)

    results = search(
        query,
        top_k=3
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
            chunk["text"][:500]
        )


# --------------------------------------------------
# SON
# --------------------------------------------------

print("\n" + "=" * 70)
print("EMBEDDING TESTİ TAMAMLANDI")
print("=" * 70)