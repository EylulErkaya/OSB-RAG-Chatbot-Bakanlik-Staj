from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationSelection(BaseModel):
    selection: int = Field(..., ge=1)


class ConversationCreate(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )