from src.database import SessionDep
from sqlmodel import Session, select
from src.schemas.user_schema import UserProfileIn
from src.models.user_models import Profile
from fastapi import HTTPException
import uuid


def get_profile_data(session: Session, user_id: uuid.UUID) -> Profile | None:
    try:
        statement = select(Profile).where(Profile.user_id == user_id)
        return session.execute(statement).scalar_one_or_none()
    except Exception as e:
        session.rollback()
        print("Error fetching profile:", e)
        return None


def update_profile_data(session: Session, profile_in: UserProfileIn) -> Profile | None:
    try:
        profile = get_profile_data(session=session, user_id=profile_in.user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile.name = profile_in.name
        profile.bio = profile_in.bio
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile

    except Exception as e:
        session.rollback()
        print("Error updating profile:", e)
        return None
        