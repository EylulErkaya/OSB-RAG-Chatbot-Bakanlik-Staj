from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models import Conversation, Message
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.rag_service import RAGService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


rag_service = RAGService()


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    # Conversation kontrolü
    conversation = db.get(
        Conversation,
        request.conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    # Kullanıcı mesajını kaydet
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # RAG
    result = rag_service.ask(
        request.message
    )

    answer_data = result.get("answer", {})

    answer = answer_data.get(
        "answer",
        "Yanıt oluşturulamadı.",
    )

    status = answer_data.get(
        "status",
        "unknown",
    )

    # Assistant mesajını kaydet
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
    )

    db.add(assistant_message)

    # Conversation güncelle
    conversation.updated_at = user_message.created_at

    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        user_message=request.message,
        answer=answer,
        status=status,
    )