from pydantic_settings import BaseSettings
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()