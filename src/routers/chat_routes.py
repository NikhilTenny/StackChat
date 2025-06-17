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
from src.managers import chat_managers as chat_manager
from src.managers.auth_managers import get_user_by_id
from src.schemas.chat_schema import CreateConversation  
router = APIRouter(prefix="/chat", tags=["chat"])
from src.utils import _get_authenticated_user_id
from src.schemas.common_schema import StandardResponse
from src.schemas.chat_schema import ConversationResponse
from src.schemas.user_schema import UserResponse


from sqlalchemy import select

@router.get("/")
def get_conversations(session: SessionDep, dependency=Depends(jwt_bearer)):
    # From dependency get the userid
    user_id = _get_authenticated_user_id(dependency)
    
    # get records from partidipants table where with the given userid
    # from that get all the conversations

    stmt = (
        select(Conversation)
            .join(Participant)
            .where(Participant.user_id == user_id)
    )
    conversation = session.scalar(stmt)
    # return the conversations
    return StandardResponse(success=True, data=[ConversationResponse.from_orm(conversation)])



def _validate_conversation_creation(session: SessionDep, creator_id: uuid.UUID, receiver_id: uuid.UUID) -> None:
    """Validate conversation creation parameters."""
    if creator_id == receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create conversation with yourself"
        )
    
    if not get_user_by_id(session=session, id=receiver_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )
    
    if chat_manager.check_existing_conversation(session=session, user_id=creator_id, receiver_id=receiver_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation already exists"
        )
@router.post("/")
def create_conversation(session: SessionDep, receiver: CreateConversation, dependency=Depends(jwt_bearer)):
    user_id = _get_authenticated_user_id(dependency)
    receiver_id = receiver.receiver_id

    _validate_conversation_creation(session=session, creator_id=user_id, receiver_id=receiver_id)

    try:
        conversation = chat_manager.create_conversation(session=session, creator_id=user_id, receiver_ids=[receiver_id])
        if conversation:
            return StandardResponse(success=True, data=ConversationResponse.from_orm(conversation))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

@router.get("/{conversation_id}")
def get_conversation_by_id(session: SessionDep, conversation_id: uuid.UUID, dependency=Depends(jwt_bearer)):
    user_id = _get_authenticated_user_id(dependency)
    
    # get records from partidipants table where with the given userid
    # from that get all the conversations

    stmt = (
        select(Conversation)
            .join(Participant)
            .where(Participant.user_id == user_id)
            .where(Conversation.id == conversation_id)
    )
    conversation = session.scalar(stmt)

    # return the conversations
    return StandardResponse(success=True, data=ConversationResponse.from_orm(conversation))

# @router.post("/send")
# def send_message(session: SessionDep, message_in: MessageIn, dependency=Depends(jwt_bearer)):
#     pass

@router.get("/search_user/{search_query}")
def search_user(session: SessionDep, search_query: str, dependency=Depends(jwt_bearer)):
    
    # get records from user table where name or email contains search_query
    stmt = select(User).where(User.name.contains(search_query) | User.email.contains(search_query))
    users = session.scalars(stmt).all()
    
    response_data = [UserResponse.from_orm(user) for user in users]
    return StandardResponse(success=True, data=response_data)