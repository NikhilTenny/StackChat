from pickle import load
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn
from src.database import engine, Base
from src.config import settings
from fastapi import APIRouter
from src.routers import auth_routes
from src.routers import user_routes
from src.routers import chat_routes
load_dotenv()

# Create database tables
# Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI(
    title="Real-Time Chat App",
    description="A backend powered by FastAPI and WebSockets",
    version="1.0.0"
)

origins = [
     "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_router = APIRouter()

api_router.include_router(auth_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(chat_routes.router)

app.include_router(api_router)

@app.get("/healthcheck")
def root():
    return {"message": "Hearty Welcome :)"}




if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)