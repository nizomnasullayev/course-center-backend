# app/api/telegram_webhook.py
from fastapi import APIRouter, Request, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.services.telegram_bot import get_telegram_service  # Change this import

router = APIRouter(prefix="/telegram-webhook", tags=["telegram-webhook"])

@router.post("/{secret}")
async def telegram_webhook(
    secret: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle Telegram bot webhook with secret verification"""
    service = get_telegram_service()  # Get service instance
    
    # Verify webhook secret
    if not service.verify_telegram_webhook(secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret"
        )
    
    # Process update in background
    background_tasks.add_task(process_telegram_update, await request.json())
    
    return {"status": "ok"}

async def process_telegram_update(data: dict):
    """Process Telegram update asynchronously"""
    try:
        from app.services.telegram_bot import get_telegram_service
        service = get_telegram_service()
        
        # Handle /start command
        if 'message' in data and 'text' in data['message']:
            text = data['message']['text']
            chat_id = str(data['message']['chat']['id'])
            
            if text.startswith('/start'):
                parts = text.split()
                if len(parts) > 1:
                    token = parts[1]
                    
                    # Connect to database
                    db = next(get_db())
                    try:
                        from app.models.user import User
                        from datetime import datetime
                        
                        user = db.query(User).filter(
                            User.telegram_link_token == token,
                            User.telegram_link_expires_at > datetime.utcnow()
                        ).first()
                        
                        if user:
                            user.telegram_chat_id = chat_id
                            user.telegram_link_token = None
                            user.telegram_link_expires_at = None
                            db.commit()
                            
                            await service.send_message(
                                chat_id,
                                "✅ <b>Successfully Connected!</b>\n\nYou will now receive notifications from your course center."
                            )
                        else:
                            await service.send_message(
                                chat_id,
                                "❌ <b>Invalid or Expired Link</b>\n\nPlease generate a new link from the course center website."
                            )
                    finally:
                        db.close()
                else:
                    await service.send_message(
                        chat_id,
                        f"🤖 <b>Welcome to Course Center Bot</b>\n\n"
                        f"Please use the link from the website to connect your account.\n\n"
                        f"Visit your profile on the course center website to generate your personal link."
                    )
    except Exception as e:
        print(f"Error processing webhook: {e}")