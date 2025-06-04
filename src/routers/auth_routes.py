
from fastapi import APIRouter, HTTPException, Depends
from src.database import SessionDep
from src.schemas.user_schema import UserSignup
from src.managers.auth_managers import get_user, create_user, create_token
from src.utils import get_hashed_password, verify_password, create_access_token, create_refresh_token
from src.auth_bearer import jwt_bearer  
from src.config import settings
import jwt
from datetime import datetime, timezone
from src.models.user_models import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=201)
def signup(user_in: UserSignup, session: SessionDep):

    user = get_user(session=session, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    
    # Create record in user table
    hashed_password = get_hashed_password(user_in.password)
    user_in.password = hashed_password
    user_record = create_user(session=session, user_in=user_in)

    if not user_record:
        raise HTTPException(status_code=500, detail="User creation failed")
    
    # return a 201 saying user created
    return {"message": "User created successfully"}



@router.post('/login')
def login(user_in: UserSignup, session: SessionDep):
    user = get_user(session=session, email=user_in.email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    if not verify_password(user_in.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    create_token(session=session, user_id=user.id, access_token=access_token, refresh_token=refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

@router.post('/logout')
def logout(session: SessionDep, dependency=Depends(jwt_bearer)):
    token = dependency
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    user_id = payload['sub']
    token_record = session.query(Token).all()
    info=[]
    for record in token_record :
        if (datetime.now(timezone.utc) - record.created_at).days >1:
            info.append(record.user_id)
    if info:
        existing_token = session.query(Token).where(Token.user_id.in_(info)).delete()
        session.commit()

    existing_token = session.query(Token).filter(Token.user_id == user_id, Token.access_token==token).first()
    if existing_token:
        existing_token.status=False
        session.add(existing_token)
        session.commit()
        session.refresh(existing_token)


    return {"message": "Logout successful"}
    
