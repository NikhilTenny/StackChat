from src.database import SessionDep
from sqlmodel import Session, select
from src.models.user_models import User, Token
from src.schemas.user_schema import UserSignup
import uuid

def get_user(session: Session, email: str) -> User | None:
    """
        Retrieve a user by their email address
    """
    try:
        statement = select(User).where(User.email == email)
        return session.execute(statement).scalar_one_or_none()
    except Exception as e:
        print("Error fetching user:", e)
        return None

def create_user(session: Session, user_in: UserSignup):
    """
        Create a new user in the database
    """
    try:
        user = User(email=user_in.email, password=user_in.password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        print("Error creating user:", e)
        return None


def create_token(session: Session, user_id: uuid.UUID, access_token: str, refresh_token: str):
    try:
        token = Token(user_id=user_id, access_token=access_token, refresh_token=refresh_token)
        session.add(token)
        session.commit()
        session.refresh(token)
        return token
    except Exception as e:
        print("Error creating token:", e)
        return None
    