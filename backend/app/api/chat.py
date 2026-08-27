from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.json_utils import sanitize_for_json
from backend.app.db.database import get_db
from backend.app.models import Conversation, Message
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.rag_service import RAGService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


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

    # Her istek için ayrı bir pipeline kullanılır. Bekleyen seçim durumu
    # Conversation üzerinde tutulduğundan, global bir pipeline farklı
    # kullanıcıların durumlarını birbirine karıştırabilir.
    rag_service = RAGService()

    if conversation.pending_query and conversation.pending_candidates:
        rag_service.restore_pending_state(
            conversation.pending_query,
            conversation.pending_candidates,
        )
        
    if conversation.pending_listing:
        rag_service.restore_pending_listing(
            conversation.pending_listing
        )

    # RAG
    result = rag_service.ask(
        request.message
    )
    
    # ==========================================
    # RAG CONVERSATION STATE
    # ==========================================

    retrieval = result.get(
        "retrieval",
        {}
    )

    retrieval_status = retrieval.get(
        "status"
    )

    # ------------------------------------------
    # AMBIGUOUS STATE
    # ------------------------------------------

    if retrieval_status == "ambiguous":

        conversation.pending_query = (
            request.message
        )

        conversation.pending_candidates = (
            sanitize_for_json(
                retrieval.get(
                    "candidates",
                    []
                )
            )
        )

        conversation.pending_listing = None

    # ------------------------------------------
    # LISTING STATE
    # ------------------------------------------

    elif retrieval_status == "listing":

        conversation.pending_listing = sanitize_for_json(
            {
                "query": retrieval.get(
                    "query",
                    request.message,
                ),
                "filters": retrieval.get(
                    "filters",
                    {}
                ),
                "offset": retrieval.get(
                    "offset",
                    0
                ),
                "limit": retrieval.get(
                    "limit",
                    10
                ),
                "total_count": retrieval.get(
                    "total_count",
                    0
                ),
            }
        )

        conversation.pending_query = None
        conversation.pending_candidates = None

    # Geçersiz seçimde mevcut adayları koru; kullanıcı yeniden seçim
    # yapabilmelidir.
    elif retrieval_status == "selection_error":

        pass

    # ------------------------------------------
    # NORMAL SUCCESS / OTHER
    # ------------------------------------------

    else:

        conversation.pending_query = None
        conversation.pending_candidates = None
        conversation.pending_listing = None

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
