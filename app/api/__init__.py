from fastapi import APIRouter
from app.api import users, auth, subject, group, group_students, lesson, attendance, payment

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(subject.router)
api_router.include_router(group.router)
api_router.include_router(group_students.router)
api_router.include_router(lesson.router)
api_router.include_router(attendance.router)
api_router.include_router(payment.router)