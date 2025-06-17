import uuid
from typing import List
from fastapi import HTTPException, status
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

def create_conversation(session: SessionDep, creator_id: uuid.UUID, receiver_ids: List[uuid.UUID]) -> Conversation | None:
    try:
        conversation = Conversation(creator_id=creator_id)
        session.add(conversation)
        session.flush()

        participants = []
        # Adding creator to participants
        receiver_ids.append(creator_id)

        for id in receiver_ids:
            participants.append(Participant(user_id=id, conv_id=conversation.id))
        
        session.add_all(participants)
        session.commit()
        session.refresh(conversation)
        
        return conversation
    except Exception as e:
        print('Ehere occured error: ', e)
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )
    