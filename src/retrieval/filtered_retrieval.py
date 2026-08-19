import chromadb
import ollama

from osb_resolver import resolve_osb


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
# FILTERED SEARCH
# ============================================================

def filtered_search(
    query: str,
    osb_name: str,
    city: str | None = None,
    chunk_type: str | None = None,
    top_k: int = 5,
):
    """
    OSB resolver + Chroma metadata filtering
    + semantic search.
    """

    # --------------------------------------------------------
    # 1. OSB RESOLUTION
    # --------------------------------------------------------

    resolved = resolve_osb(
        osb_name,
        city
    )

    # --------------------------------------------------------
    # BULUNAMADI
    # --------------------------------------------------------

    if resolved["status"] == "not_found":

        return {
            "status": "not_found",
            "results": []
        }

    # --------------------------------------------------------
    # BELİRSİZ
    # --------------------------------------------------------

    if resolved["status"] == "ambiguous":

        return {
            "status": "ambiguous",
            "candidates": resolved["candidates"],
            "results": []
        }

    # --------------------------------------------------------
    # UNIQUE
    # --------------------------------------------------------

    osb_id = resolved["osb_id"]

    # --------------------------------------------------------
    # METADATA FILTER
    # --------------------------------------------------------
    if chunk_type:
        where =  {
            "$and" : [
                {
                    "osb_id": osb_id
                },
                {
                    "chunk_type": chunk_type
                }
            ]
        }
    else:
        where = {
            "osb_id": osb_id
        }

    # --------------------------------------------------------
    # QUERY EMBEDDING
    # --------------------------------------------------------

    query_embedding = create_query_embedding(
        query
    )

    # --------------------------------------------------------
    # CHROMA SEARCH
    # --------------------------------------------------------

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k,
        where=where,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    return {
        "status": "success",
        "osb_id": osb_id,
        "osb_name": resolved["osb_name"],
        "results": results,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    tests = [

        {
            "query":
                "Malatya-Güney OSB'de kaç fabrika üretim yapıyor?",
            "osb_name":
                "Malatya-Güney",
            "city":
                "Malatya",
            "chunk_type":
                "osb_employment",
        },

        {
            "query":
                "Malatya-Yeni OSB'de kaç fabrika üretim yapıyor?",
            "osb_name":
                "Malatya-Yeni",
            "city":
                "Malatya",
            "chunk_type":
                "osb_employment",
        },

        {
            "query":
                "Malatya OSB'de kaç fabrika üretim yapıyor?",
            "osb_name":
                "Malatya OSB",
            "city":
                "Malatya",
            "chunk_type":
                "osb_employment",
        },
    ]


    print("=" * 70)
    print("FILTERED RETRIEVAL TESTİ")
    print("=" * 70)


    for test in tests:

        print("\n" + "-" * 70)

        print(
            f"SORU: {test['query']}"
        )

        print("-" * 70)

        result = filtered_search(
            query=test["query"],
            osb_name=test["osb_name"],
            city=test["city"],
            chunk_type=test["chunk_type"],
            top_k=5,
        )

        # ----------------------------------------------------
        # AMBIGUOUS
        # ----------------------------------------------------

        if result["status"] == "ambiguous":

            print(
                "\n⚠️ OSB BELİRSİZ"
            )

            print(
                "Aday kayıtlar:"
            )

            for candidate in result["candidates"]:

                print(
                    f"  ID {candidate['id']} | "
                    f"{candidate['name']} | "
                    f"{candidate['district']}"
                )

            continue

        # ----------------------------------------------------
        # NOT FOUND
        # ----------------------------------------------------

        if result["status"] == "not_found":

            print(
                "\n❌ OSB BULUNAMADI"
            )

            continue

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        print(
            f"\n✓ OSB ID: {result['osb_id']}"
        )

        print(
            f"✓ OSB: {result['osb_name']}"
        )

        documents = result["results"]["documents"][0]
        metadatas = result["results"]["metadatas"][0]
        distances = result["results"]["distances"][0]

        print(
            f"✓ Sonuç sayısı: {len(documents)}"
        )

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
                "\nTEXT:"
            )

            print(
                document[:700]
            )


    print("\n" + "=" * 70)
    print("TEST TAMAMLANDI")
    print("=" * 70)