

from sqlalchemy import func, TIMESTAMP, String, UUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from typing import List
from datetime import datetime
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Conversation(Base):
    __tablename__ = "conversation"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    creator_id : Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    title: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    creator: Mapped['User'] = relationship("User", back_populates="created_conversations")
    participants: Mapped[List['Participant']] = relationship("Participant", back_populates="conv")
    

class Participant(Base):
    __tablename__ = "participant"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    conv_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversation.id"))


    user: Mapped['User'] = relationship("User", back_populates="chat_participants")
    conv: Mapped['Conversation'] = relationship("Conversation", back_populates="participants")