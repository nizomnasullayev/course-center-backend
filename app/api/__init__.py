from fastapi import APIRouter
from app.api import users, auth, subject, group, group_students, lesson, attendance, payment, telegram, telegram_webhook, course_centers

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(course_centers.router)
api_router.include_router(subject.router)
api_router.include_router(group.router)
api_router.include_router(group_students.router)
api_router.include_router(lesson.router)
api_router.include_router(attendance.router)
api_router.include_router(payment.router)
api_router.include_router(telegram.router)
api_router.include_router(telegram_webhook.router)