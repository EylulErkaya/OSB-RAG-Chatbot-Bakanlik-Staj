from src.generation.context_builder import ContextBuilder
from src.retrieval.retrieval_pipeline import retrieve


# ============================================================
# CONTEXT BUILDER TESTİ
# ============================================================

builder = ContextBuilder()

queries = [
    "Malatya-Güney OSB'de kaç boş parsel var?",
    "Malatya-Güney OSB'de kaç fabrika üretim yapıyor?",
    "Malatya-Güney OSB'de kaç kişi istihdam ediliyor?",
    "Malatya-Güney OSB hangi bölgede bulunuyor?",
    "Malatya-Güney OSB'de gıda sektöründe kaç kişi çalışıyor?",
]


print("=" * 70)
print("CONTEXT BUILDER TESTİ")
print("=" * 70)


for query in queries:

    print("\n" + "=" * 70)
    print(f"SORU: {query}")
    print("=" * 70)

    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    retrieval_result = retrieve(
        query=query
    )

    print(
        f"\nRetrieval status: "
        f"{retrieval_result.get('status')}"
    )

    print(
        f"Intent: "
        f"{retrieval_result.get('intent')}"
    )

    print(
        f"Chunk type: "
        f"{retrieval_result.get('chunk_type')}"
    )

    print(
        f"OSB: "
        f"{retrieval_result.get('osb_name')}"
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context_result = builder.build(
        retrieval_result
    )

    print(
        f"\nContext status: "
        f"{context_result.get('status')}"
    )

    print(
        f"LLM allowed: "
        f"{context_result.get('llm_allowed')}"
    )

    # --------------------------------------------------------
    # MESAJ
    # --------------------------------------------------------

    if context_result.get("message"):

        print(
            f"\nMESSAGE:\n"
            f"{context_result['message']}"
        )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = context_result.get(
        "context",
        ""
    )

    if context:

        print(
            "\nCONTEXT:"
        )

        print(
            context
        )


print("\n" + "=" * 70)
print("TEST TAMAMLANDI")
print("=" * 70)