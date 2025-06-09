from fastapi import APIRouter, HTTPException, Depends
from src.database import SessionDep
from src.config import settings
from datetime import datetime, timezone
from src.models.user_models import Token
from src.auth_bearer import jwt_bearer
import jwt
from src.managers.user_manager import get_profile_data, update_profile_data
from src.schemas.user_schema import UserProfileInBase, UserProfileIn

router = APIRouter(prefix="/user", tags=["user"])

@router.get('/profile')
def get_profile(session: SessionDep, dependency=Depends(jwt_bearer)):
    payload = jwt.decode(dependency, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    print(payload)
    user_id = payload['sub']
    profile = get_profile_data(session=session, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"data": profile}



@router.put('/profile')
def update_profile(session: SessionDep, profile_in: UserProfileInBase, dependency=Depends(jwt_bearer)):
    payload = jwt.decode(dependency, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    user_id = payload['sub']
    profile_in = UserProfileIn(user_id=user_id, name=profile_in.name, bio=profile_in.bio)
    profile = update_profile_data(session=session, profile_in=profile_in)
    return {"data": profile}
