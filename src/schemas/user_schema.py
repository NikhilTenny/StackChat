from pydantic import BaseModel
from pydantic.networks import EmailStr
import uuid

class UserSignup(BaseModel):
    email: EmailStr
    password: str 


class UserProfileInBase(BaseModel):
    name: str | None = None
    bio: str | None = None
class UserProfileIn(UserProfileInBase):
    user_id: uuid.UUID