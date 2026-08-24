from backend.app.services.rag_service import RAGService


def main():
    service = RAGService()

    result = service.ask(
        "Malatya-Güney OSB'de kaç boş parsel var?"
    )

    print("✓ RAG Service çalıştı")
    print()
    print("Retrieval status:")
    print(result["retrieval"]["status"])

    print()
    print("Cevap:")
    print(result["answer"]["answer"])


if __name__ == "__main__":
    main()