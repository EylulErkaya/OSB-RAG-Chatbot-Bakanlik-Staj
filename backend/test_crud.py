from backend.app.db.database import SessionLocal
from backend.app.models import Conversation, Message


def main():
    db = SessionLocal()

    try:
        # -----------------------------------------
        # 1. Conversation oluştur
        # -----------------------------------------

        conversation = Conversation(
            title="SQLAlchemy Test Sohbeti"
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        print(
            f"✓ Conversation oluşturuldu: "
            f"{conversation.id}"
        )

        # -----------------------------------------
        # 2. User mesajı oluştur
        # -----------------------------------------

        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content="Malatya OSB'de kaç boş parsel var?"
        )

        db.add(user_message)

        # -----------------------------------------
        # 3. Assistant mesajı oluştur
        # -----------------------------------------

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content="Bu bir SQLAlchemy test cevabıdır."
        )

        db.add(assistant_message)

        db.commit()

        print("✓ User mesajı kaydedildi")
        print("✓ Assistant mesajı kaydedildi")

        # -----------------------------------------
        # 4. Conversation'ı tekrar oku
        # -----------------------------------------

        saved_conversation = db.get(
            Conversation,
            conversation.id
        )

        print(
            f"\n✓ Conversation bulundu: "
            f"{saved_conversation.title}"
        )

        # -----------------------------------------
        # 5. Mesajları oku
        # -----------------------------------------

        for message in saved_conversation.messages:
            print(
                f"  [{message.role}] "
                f"{message.content}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()