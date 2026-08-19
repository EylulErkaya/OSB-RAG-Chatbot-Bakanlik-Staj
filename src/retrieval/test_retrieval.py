import chromadb
import ollama


# ============================================================
# AYARLAR
# ============================================================

CHROMA_PATH = "data/vectorstore/chroma"
COLLECTION_NAME = "osb_knowledge_base"

EMBEDDING_MODEL = "nomic-embed-text:v1.5"


# ============================================================
# CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


print("=" * 70)
print("CHROMADB RETRIEVAL TESTİ")
print("=" * 70)

print(
    f"Collection: {COLLECTION_NAME}"
)

print(
    f"Kayıt sayısı: {collection.count()}"
)


# ============================================================
# QUERY EMBEDDING
# ============================================================

def create_query_embedding(query: str):

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=query
    )

    return response["embeddings"][0]


# ============================================================
# SEARCH
# ============================================================

def search(
    query: str,
    top_k: int = 5
):

    query_embedding = create_query_embedding(
        query
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    return results


# ============================================================
# TEST SORULARI
# ============================================================

queries = [

    "Malatya OSB'de kaç boş parsel var?",

    "Malatya OSB hangi bölgede bulunuyor?",

    "Malatya OSB'de kaç kişi istihdam ediliyor?",

    "Malatya OSB'de gıda sektöründe kaç kişi çalışıyor?",

    "Malatya OSB'de kaç fabrika üretim yapıyor?",

]


# ============================================================
# TEST
# ============================================================

for query in queries:

    print("\n" + "-" * 70)

    print(
        f"SORU: {query}"
    )

    print("-" * 70)

    results = search(
        query,
        top_k=5
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for rank, (
        document,
        metadata,
        distance
    ) in enumerate(
        zip(
            documents,
            metadatas,
            distances
        ),
        start=1
    ):

        print(
            f"\n#{rank}"
        )

        print(
            f"Distance: {distance:.4f}"
        )

        print(
            f"Chunk type: "
            f"{metadata.get('chunk_type')}"
        )

        print(
            f"OSB ID: "
            f"{metadata.get('osb_id')}"
        )

        print(
            f"OSB: "
            f"{metadata.get('osb_adi')}"
        )

        print(
            f"İl: "
            f"{metadata.get('il')}"
        )

        print("\nTEXT:")

        print(
            document[:500]
        )


print("\n" + "=" * 70)

print(
    "RETRIEVAL TESTİ TAMAMLANDI"
)

print("=" * 70)