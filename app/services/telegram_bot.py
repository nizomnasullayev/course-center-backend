# app/services/telegram_bot.py
import logging
import hmac
import hashlib
import secrets
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.config import settings

logger = logging.getLogger(__name__)


class TelegramBotService:
    def __init__(self):
        """Initialize Telegram bot service with settings from config"""
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.bot_username = settings.TELEGRAM_BOT_USERNAME
        self.webhook_secret = settings.TELEGRAM_WEBHOOK_SECRET
        self.link_expire_minutes = settings.TELEGRAM_LINK_EXPIRE_MINUTES
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def generate_telegram_link(self, user_id: UUID) -> Tuple[str, str, datetime]:
        """Generate a unique link for user to connect their Telegram"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=self.link_expire_minutes)
        deep_link = f"https://t.me/{self.bot_username}?start={token}"
        return token, deep_link, expires_at
    
    def verify_telegram_webhook(self, secret: str) -> bool:
        """Verify webhook secret for security"""
        return hmac.compare_digest(secret, self.webhook_secret)
    
    async def send_message(self, chat_id: str, text: str) -> Tuple[bool, Optional[str]]:
        """Send a message to a Telegram user"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
                async with session.post(f"{self.api_url}/sendMessage", json=payload) as resp:
                    if resp.status == 200:
                        return True, None
                    else:
                        error = await resp.text()
                        logger.error(f"Telegram API error: {error}")
                        return False, error
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False, str(e)
    
    async def notify_user(
        self, 
        db: Session, 
        user_id: UUID, 
        notification_type: str,
        title: str, 
        message: str
    ):
        """Send notification to a single user and log it"""
        from app.models.user import User
        from app.models.notification_log import NotificationLog, NotificationType, NotificationStatus
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.telegram_chat_id or not user.telegram_notifications_enabled:
            return
        
        log = NotificationLog(
            user_id=user_id,
            notification_type=NotificationType(notification_type),
            content=f"{title}\n\n{message}",
            status=NotificationStatus.PENDING
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        full_message = f"<b>{title}</b>\n\n{message}"
        success, error = await self.send_message(user.telegram_chat_id, full_message)
        
        log.status = NotificationStatus.SENT if success else NotificationStatus.FAILED
        if error:
            log.error_message = error
        log.sent_at = datetime.utcnow()
        db.commit()
        
        return success


# Singleton instance
_telegram_service = None


def get_telegram_service():
    """Get or create Telegram bot service instance"""
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramBotService()
    return _telegram_service