from fastapi import APIRouter
from app.api import users, auth, subject, group, group_students

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(subject.router)
api_router.include_router(group.router)
api_router.include_router(group_students.router)