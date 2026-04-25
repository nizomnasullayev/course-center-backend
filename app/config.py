# app/config.py
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = str(PROJECT_ROOT / "firebase-credentials.json")

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""
    TELEGRAM_LINK_EXPIRE_MINUTES: int = 60
    TELEGRAM_USE_POLLING: bool = False
    APP_BASE_URL: str = "http://localhost:8000"  # Added this field
    
    # Use model_config instead of Config class (Pydantic v2)
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # This allows extra fields in .env without errors
    )


settings = Settings()