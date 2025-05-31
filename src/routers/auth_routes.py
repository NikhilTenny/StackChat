
from fastapi import APIRouter, HTTPException



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup():
    pass