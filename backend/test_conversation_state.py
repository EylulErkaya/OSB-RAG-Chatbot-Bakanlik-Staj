from backend.app.db.database import SessionLocal
from backend.app.models import Conversation


def main():
    db = SessionLocal()

    conversation = Conversation(
        title="Ambiguous State Test"
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    conversation.pending_query = (
        "Malatya OSB'de kaç fabrika üretim yapıyor?"
    )

    conversation.pending_candidates = [
        {
            "id": 1,
            "name": "Malatya OSB",
            "city": "Malatya",
            "type": "Sanayi",
        },
        {
            "id": 2,
            "name": "Malatya OSB",
            "city": "Malatya",
            "type": "Organize",
        },
    ]

    db.commit()
    db.refresh(conversation)

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