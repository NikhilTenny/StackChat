from pydantic import BaseModel
from pydantic.networks import EmailStr


class UserSignup(BaseModel):
    email: EmailStr
    password: str 