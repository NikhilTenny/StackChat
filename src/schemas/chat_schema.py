from pydantic import BaseModel
from pydantic.networks import EmailStr
import uuid
from datetime import datetime


class CreateConversation(BaseModel):
    receiver_id: uuid.UUID

class ConversationResponse(BaseModel):
    creator_id: uuid.UUID
    title: str | None = None
    updated_at: datetime

    class Config:
        from_attributes = True