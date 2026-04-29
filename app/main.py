# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.config import settings  # Remove the duplicate comment

app = FastAPI(
    title="Course Center API",
    description="Backend API for Course Center Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",              # local dev
        "https://course-center-seven.vercel.app",  # frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Start background services"""
    if settings.TELEGRAM_USE_POLLING:
        from app.services.telegram_poller import start_telegram_poller
        start_telegram_poller()

@app.get("/")
def root():
    return {
        "message": "Course Center API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}