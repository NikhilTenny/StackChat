from pydantic import BaseModel
from pydantic.networks import EmailStr
import uuid
from datetime import datetime

class UserSignup(BaseModel):
    email: EmailStr
    password: str 


class UserProfileInBase(BaseModel):
    name: str | None = None
    bio: str | None = None
class UserProfileIn(UserProfileInBase):
    user_id: uuid.UUID


class ProfileResponse(BaseModel):
    name: str | None
    bio: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str | None
    bio: str | None
    created_at: datetime

    class Config:
        from_attributes = True