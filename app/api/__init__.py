from fastapi import APIRouter
from app.api import users, auth, subject

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(subject.router)