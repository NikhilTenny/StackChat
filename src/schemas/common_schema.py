from typing import Optional, Any
from pydantic import BaseModel


class ResponseBase(BaseModel):
    success: bool
    message: str = ""
    error: str | None = None


class StandardResponse(ResponseBase):
    data: Optional[Any] = None