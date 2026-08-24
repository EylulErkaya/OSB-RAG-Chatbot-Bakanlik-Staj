from backend.app.db.database import SessionLocal
from backend.app.models import Conversation
from src.generation.rag_pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()
    db = SessionLocal()

    query = "Malatya OSB'de kaç fabrika üretim yapıyor?"

    print("Soru:")
    print(query)

    result = pipeline.ask(query)

    print()
    print("RAG status:")
    print(result["retrieval"]["status"])

    print()
    print("RAG sonucu:")
    print(result)

    if result["retrieval"]["status"] != "ambiguous":
        print()
        print("❌ Test için ambiguous sonuç alınamadı.")
        db.close()
        return

    conversation = Conversation(
        title="Ambiguous DB Test"
    )

    conversation.pending_query = query
    candidates = result["retrieval"]["candidates"]

    candidate_state = [
        {
            "id": candidate["id"],
            "name": candidate["name"],
            "city": candidate["city"],
            "district": candidate["district"],
            "region": candidate["region"],
        }
        for candidate in candidates
    ]

    conversation.pending_candidates = candidate_state

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    print()
    print("✓ Conversation oluşturuldu:")
    print(conversation.id)

    print()
    print("✓ Pending query:")
    print(conversation.pending_query)

    print()
    print("✓ Pending candidates:")
    print(conversation.pending_candidates)

    db.close()


if __name__ == "__main__":
    main()