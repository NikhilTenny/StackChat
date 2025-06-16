import uuid

from fastapi import HTTPException
from sqlmodel import Session, select, func
from src.database import SessionDep
from src.models.chat_models import Conversation, Participant



def check_existing_conversation(session: SessionDep, user_id: uuid.UUID, receiver_id: uuid.UUID) -> bool:

    smt = (
        select(Conversation)
        .join(Participant, Participant.conv_id == Conversation.id)
        .where(Participant.user_id.in_([user_id, receiver_id]))
        .group_by(Conversation)
        .having(func.count(Participant.id) == 2)
    )
    conversation = session.scalar(smt)
    if conversation:
        return True
    return False