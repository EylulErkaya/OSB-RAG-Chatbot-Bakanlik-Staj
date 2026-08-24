import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models import Conversation, Message
from backend.app.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationSelection,
    MessageResponse,
)

from backend.app.services.rag_service import RAGService


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationResponse,
)
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
):
    conversation = Conversation(
        title=data.title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get(
    "",
    response_model=list[ConversationResponse],
)
def get_conversations(
    db: Session = Depends(get_db),
):
    conversations = (
        db.query(Conversation)
        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )

    return conversations


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = db.get(
        Conversation,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation


@router.delete(
    "/{conversation_id}",
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = db.get(
        Conversation,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    db.delete(conversation)
    db.commit()

    return {
        "message": "Conversation deleted",
        "id": conversation_id,
    }
    
@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = db.get(
        Conversation,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.asc()
        )
        .all()
    )

    return messages

@router.post(
    "/{conversation_id}/select",
)
def select_conversation_candidate(
    conversation_id: int,
    data: ConversationSelection,
    db: Session = Depends(get_db),
):
    try:
        conversation = db.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        if not conversation.pending_candidates:
            raise HTTPException(
                status_code=400,
                detail="No pending candidate selection",
            )

        if not conversation.pending_query:
            raise HTTPException(
                status_code=400,
                detail="No pending query",
            )

        candidates = conversation.pending_candidates

        selection_index = data.selection - 1

        if (
            selection_index < 0
            or selection_index >= len(candidates)
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid selection. Choose between 1 and {len(candidates)}.",
            )

        selected_candidate = candidates[selection_index]

        print("SEÇİLEN ADAY:")
        print(selected_candidate)

        print("PENDING QUERY:")
        print(conversation.pending_query)

        rag_service = RAGService()

        rag_service.pipeline.pending_query = conversation.pending_query
        rag_service.pipeline.pending_candidates = candidates

        result = rag_service.pipeline.ask(
            str(data.selection)
        )

        print("RAG RESULT:")
        print(result)

        answer = result.get("answer", {}).get(
            "answer",
            "Yanıt oluşturulamadı.",
        )

        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=conversation.pending_query,
        )

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
        )

        db.add(user_message)
        db.add(assistant_message)

        conversation.pending_query = None
        conversation.pending_candidates = None

        db.commit()

        return {
            "conversation_id": conversation.id,
            "status": "success",
            "selection": data.selection,
            "selected_candidate": selected_candidate,
            "answer": answer,
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        print("\n" + "=" * 60)
        print("SELECT ENDPOINT HATASI")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )