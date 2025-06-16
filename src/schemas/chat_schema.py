from pydantic import BaseModel
from pydantic.networks import EmailStr
import uuid


class CreateConversation(BaseModel):
    receiver_id: uuid.UUID