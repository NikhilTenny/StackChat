
from fastapi import APIRouter, HTTPException
from src.database import SessionDep
from src.schemas.user_schema import UserSignup
from src.managers.auth_managers import get_user, create_user, create_token
from src.utils import get_hashed_password, verify_password, create_access_token, create_refresh_token


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

    
