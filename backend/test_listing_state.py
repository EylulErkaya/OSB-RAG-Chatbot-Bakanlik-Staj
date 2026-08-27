from backend.app.db.database import SessionLocal
from backend.app.models import Conversation


def main():
    db = SessionLocal()

    try:
        conversation = Conversation(
            title="Listing State Test"
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        conversation.pending_listing = {
            "query": "Doğu Anadolu'daki OSB'leri listele",
            "filters": {
                "city": None,
                "district": None,
                "region": "Doğu Anadolu",
                "osb_type": None,
                "stage": None,
                "investment_program": None,
                "earthquake_region": None,
                "incentive_region": None,
            },
            "offset": 0,
            "limit": 10,
            "total_count": 77,
        }

        db.commit()
        db.refresh(conversation)

        print("✓ Conversation oluşturuldu:")
        print(conversation.id)

        print("\n✓ Pending listing:")
        print(conversation.pending_listing)

        assert conversation.pending_listing is not None
        assert conversation.pending_listing["offset"] == 0
        assert conversation.pending_listing["limit"] == 10
        assert conversation.pending_listing["total_count"] == 77
        assert (
            conversation.pending_listing["query"]
            == "Doğu Anadolu'daki OSB'leri listele"
        )

        print("\n✓ Listing state PostgreSQL'e başarıyla kaydedildi.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
