# app/api/telegram.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.config import settings
from app.services.telegram_bot import get_telegram_service  # Change this import

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Don't create instance here - use get_telegram_service() instead
# telegram_service = TelegramBotService(...)  # REMOVE THIS LINE

@router.post("/generate-link")
def generate_telegram_link(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a unique link for user to connect their Telegram"""
    service = get_telegram_service()  # Get service instance
    
    # Generate new token and link
    token, deep_link, expires_at = service.generate_telegram_link(current_user.id)
    
    # Save to user
    current_user.telegram_link_token = token
    current_user.telegram_link_expires_at = expires_at
    db.commit()
    
    return {
        "telegram_link": deep_link,
        "expires_at": expires_at.isoformat(),
        "expires_in_minutes": settings.TELEGRAM_LINK_EXPIRE_MINUTES,
        "instructions": f"1. Open Telegram\n2. Search for @{settings.TELEGRAM_BOT_USERNAME}\n3. Click Start or open this link"
    }

@router.post("/disconnect")
def disconnect_telegram(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect Telegram account"""
    current_user.telegram_chat_id = None
    current_user.telegram_notifications_enabled = True
    db.commit()
    
    return {"message": "Telegram disconnected successfully"}

@router.post("/toggle-notifications")
def toggle_notifications(
    enabled: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enable/disable Telegram notifications"""
    current_user.telegram_notifications_enabled = enabled
    db.commit()
    
    return {"notifications_enabled": enabled}

@router.get("/status")
def get_telegram_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current Telegram connection status"""
    return {
        "connected": current_user.telegram_chat_id is not None,
        "notifications_enabled": current_user.telegram_notifications_enabled,
        "bot_username": settings.TELEGRAM_BOT_USERNAME
    }