from uuid import UUID
import uuid

import jwt

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from src.auth_bearer import jwt_bearer
from src.config import settings
from src.database import SessionDep
from src.models.chat_models import Conversation, Participant
from src.models.user_models import User
from src.managers.chat_managers import check_existing_conversation
from src.schemas.chat_schema import CreateConversation
router = APIRouter(prefix="/chat", tags=["chat"])


from sqlalchemy import select

@router.get("/")
def get_conversations(session: SessionDep, dependency=Depends(jwt_bearer)):
    # From dependency get the userid
    payload = jwt.decode(dependency, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    user_id = payload['sub']
    
    # get records from partidipants table where with the given userid
    # from that get all the conversations

    stmt = (
        select(Conversation)
            .join(Participant)
            .where(Participant.user_id == user_id)
    )
    conversation = session.scalar(stmt)
    print()
    # return the conversations
    return {"data": conversation}


@router.post("/")
def create_conversation(session: SessionDep, receiver: CreateConversation, dependency=Depends(jwt_bearer)):
    payload = jwt.decode(dependency, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    user_id = payload['sub']

    # Prevent self-conversation
    if user_id == receiver.receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create conversation with yourself"
        )

    # Check if receiver exists
    receiver = select(User).where(User.id == receiver.receiver_id)
    receiver_user = session.scalar(receiver)
    
    if not receiver_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )
    receiver_id = receiver_user.id 

    if check_existing_conversation(session=session, user_id=user_id, receiver_id=receiver_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation already exists"
        )
    # create a record in conversation and participant table
    try:
        conversation = Conversation(creator_id=user_id)
        session.add(conversation)
        session.flush()

        session.add_all([
            Participant(user_id=user_id, conv_id=conversation.id),
            Participant(user_id=receiver_id, conv_id=conversation.id)
        ])
        session.commit()
        session.refresh(conversation)
        return {"data": conversation}
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )    

@router.get("/{conversation_id}")
def get_conversation_by_id(session: SessionDep, conversation_id: uuid.UUID, dependency=Depends(jwt_bearer)):
    pass

# @router.post("/send")
# def send_message(session: SessionDep, message_in: MessageIn, dependency=Depends(jwt_bearer)):
#     pass

@router.get("/search_user/{search_query}")
def search_user(session: SessionDep, search_query: str, dependency=Depends(jwt_bearer)):
    payload = jwt.decode(dependency, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    user_id = payload['sub']
    
    # get records from user table where name or email contains search_query
    stmt = select(User).where(User.name.contains(search_query) | User.email.contains(search_query))
    users = session.scalars(stmt).all()
    
    # return the users
    return {"data": users}