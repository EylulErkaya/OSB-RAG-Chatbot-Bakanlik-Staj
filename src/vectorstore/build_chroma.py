import json
import pickle
from pathlib import Path

import chromadb


# ============================================================
# AYARLAR
# ============================================================

CHUNKS_PATH = Path("data/documents/chunks.jsonl")
EMBEDDINGS_PATH = Path("data/embeddings/embeddings.pkl")
CHROMA_PATH = Path("data/vectorstore/chroma")

COLLECTION_NAME = "osb_knowledge_base"

BATCH_SIZE = 500


# ============================================================
# DOSYA KONTROLLERİ
# ============================================================

print("=" * 70)
print("CHROMADB INDEX OLUŞTURMA")
print("=" * 70)

if not CHUNKS_PATH.exists():
    raise FileNotFoundError(
        f"Chunk dosyası bulunamadı: {CHUNKS_PATH}"
    )

if not EMBEDDINGS_PATH.exists():
    raise FileNotFoundError(
        f"Embedding dosyası bulunamadı: {EMBEDDINGS_PATH}"
    )


# ============================================================
# CHUNK'LARI OKU
# ============================================================

print("\n[1/5] Chunk'lar okunuyor...")

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


# ============================================================
# EMBEDDING'LERİ OKU
# ============================================================

print("\n[2/5] Embedding'ler okunuyor...")

with open(
    EMBEDDINGS_PATH,
    "rb"
) as file:

    embedding_data = pickle.load(file)


embeddings = embedding_data["embeddings"]

model_name = embedding_data.get(
    "model",
    "unknown"
)

print(f"Embedding sayısı: {len(embeddings)}")
print(f"Embedding modeli: {model_name}")


# ============================================================
# EŞLEŞME KONTROLÜ
# ============================================================

print("\n[3/5] Veri eşleşmesi kontrol ediliyor...")

if len(chunks) != len(embeddings):

    raise ValueError(
        f"Chunk ve embedding sayıları eşleşmiyor!\n"
        f"Chunk: {len(chunks)}\n"
        f"Embedding: {len(embeddings)}"
    )

print(
    f"✓ {len(chunks)} chunk "
    f"↔ {len(embeddings)} embedding"
)


# ============================================================
# CHUNK ID KONTROLÜ
# ============================================================

chunk_ids = [
    chunk["chunk_id"]
    for chunk in chunks
]

if len(chunk_ids) != len(set(chunk_ids)):

    raise ValueError(
        "Duplicate chunk_id bulundu!"
    )

print(
    f"✓ {len(chunk_ids)} benzersiz chunk ID"
)


# ============================================================
# CHROMA CLIENT
# ============================================================

print("\n[4/5] ChromaDB başlatılıyor...")

CHROMA_PATH.mkdir(
    parents=True,
    exist_ok=True
)

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "description": "OSB RAG Knowledge Base",
        "embedding_model": model_name,
        "embedding_dimension": len(embeddings[0]),
    }
)

print(
    f"Collection: {COLLECTION_NAME}"
)

print(
    f"Mevcut kayıt: {collection.count()}"
)


# ============================================================
# VERİLERİ CHROMA'YA AKTAR
# ============================================================

print("\n[5/5] ChromaDB'ye kayıtlar ekleniyor...")

total = len(chunks)

for start in range(
    0,
    total,
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        total
    )

    batch_chunks = chunks[start:end]
    batch_embeddings = embeddings[start:end]

    ids = [
        chunk["chunk_id"]
        for chunk in batch_chunks
    ]

    documents = [
        chunk["text"]
        for chunk in batch_chunks
    ]

    metadatas = []

    for chunk in batch_chunks:

        metadata = chunk["metadata"]

        # Chroma metadata sadece scalar değerleri
        # kabul eder. Bu nedenle güvenli bir sözlük
        # oluşturuyoruz.

        clean_metadata = {}

        for key, value in metadata.items():

            if value is None:
                continue

            if isinstance(
                value,
                (str, int, float, bool)
            ):
                clean_metadata[key] = value

            else:
                clean_metadata[key] = str(value)

        metadatas.append(
            clean_metadata
        )

    collection.upsert(
        ids=ids,
        embeddings=batch_embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(
        f"{end:>6}/{total} "
        f"(%{end / total * 100:6.2f})"
    )


# ============================================================
# SON KONTROL
# ============================================================

final_count = collection.count()

print("\n" + "=" * 70)
print("CHROMADB SONUCU")
print("=" * 70)

print(
    f"Beklenen kayıt : {total}"
)

print(
    f"Chroma kayıt    : {final_count}"
)

print(
    f"Embedding boyutu: {len(embeddings[0])}"
)

print(
    f"Embedding modeli: {model_name}"
)

print(
    f"Collection      : {COLLECTION_NAME}"
)

print(
    f"Database yolu   : {CHROMA_PATH}"
)


if final_count == total:

    print("\n🎉 CHROMADB INDEX BAŞARIYLA OLUŞTURULDU!")

else:

    raise RuntimeError(
        "ChromaDB kayıt sayısı beklenen değerle eşleşmiyor!"
    )