# app/services/telegram_poller.py - Complete working version

import threading
import time
import requests
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.group_student import GroupStudent
from app.models.lesson import Lesson
from app.models.attendance import Attendance
from app.models.payment import Payment
from app.config import settings

class SimpleTelegramPoller:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.bot_username = settings.TELEGRAM_BOT_USERNAME
        self.last_update_id = 0
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.running = True
    
    def send_message(self, chat_id: str, text: str, show_keyboard=False, is_main_menu=False):
        """Send a message to a Telegram user"""
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            # Add keyboard if requested
            if show_keyboard or is_main_menu:
                keyboard = self.get_main_keyboard() if is_main_menu else self.get_main_keyboard()
                payload["reply_markup"] = json.dumps(keyboard)
            
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"Send message error: {response.text}")
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_main_keyboard(self):
        """Create main menu keyboard with buttons"""
        return {
            "keyboard": [
                [{"text": "📚 Kurslarim"}, {"text": "📅 Jadvalim"}],
                [{"text": "💰 To'lovlarim"}, {"text": "⭐️ Baholarim"}],
                [{"text": "📝 Vazifalarim"}, {"text": "❓ Yordam"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
    
    def remove_keyboard(self):
        """Remove keyboard"""
        return {"remove_keyboard": True}
    
    def get_updates(self):
        """Get updates from Telegram"""
        try:
            params = {"offset": self.last_update_id + 1, "timeout": 30}
            response = requests.get(
                f"{self.api_url}/getUpdates", 
                params=params, 
                timeout=35
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('result', [])
            return []
        except Exception as e:
            print(f"Error getting updates: {e}")
            return []
    
    def get_user_by_chat_id(self, db, chat_id):
        """Get user by Telegram chat ID"""
        return db.query(User).filter(User.telegram_chat_id == chat_id).first()
    
    def get_student_groups(self, db, student_id):
        """Get all groups for a student"""
        enrollments = db.query(GroupStudent).filter(
            GroupStudent.student_id == student_id
        ).all()
        return [e.group for e in enrollments]
    
    def process_message(self, db, chat_id, text):
        """Process text messages and buttons"""
        user = self.get_user_by_chat_id(db, chat_id)
        if not user:
            self.send_message(chat_id, "❌ Iltimos, avval profilingizni ulang!")
            return
        
        # Main menu buttons
        if text == "📚 Kurslarim" or text == "/courses":
            groups = self.get_student_groups(db, user.id)
            if groups:
                response = "📚 <b>Sizning kurslaringiz:</b>\n\n"
                for i, group in enumerate(groups, 1):
                    response += f"{i}. <b>{group.name}</b>\n"
                    response += f"   📖 Fan: {group.subject.name if group.subject else 'N/A'}\n"
                    response += f"   👨‍🏫 Ustoz: {group.teacher.full_name if group.teacher else 'N/A'}\n"
                    response += f"   📅 Jadval: {group.schedule}\n\n"
            else:
                response = "❌ Siz hali hech qanday kursga yozilmagansiz."
            self.send_message(chat_id, response)
        
        elif text == "📅 Jadvalim" or text == "/schedule":
            groups = self.get_student_groups(db, user.id)
            if groups:
                response = "📅 <b>Haftalik jadvalingiz:</b>\n\n"
                for group in groups:
                    response += f"📚 <b>{group.name}</b>\n"
                    
                    # Get upcoming lessons
                    upcoming_lessons = db.query(Lesson).filter(
                        Lesson.group_id == group.id,
                        Lesson.lesson_date >= datetime.now(),
                        Lesson.status != "cancelled"
                    ).order_by(Lesson.lesson_date).limit(5).all()
                    
                    if upcoming_lessons:
                        for lesson in upcoming_lessons:
                            lesson_date = lesson.lesson_date.strftime('%d.%m %H:%M')
                            response += f"   • {lesson_date}: {lesson.topic or 'Mavzu belgilanmagan'}\n"
                    else:
                        response += "   • Yangi darslar rejalashtirilmagan\n"
                    response += "\n"
            else:
                response = "❌ Siz hali hech qanday kursga yozilmagansiz."
            self.send_message(chat_id, response)
        
        elif text == "💰 To'lovlarim" or text == "/payments":
            payments = db.query(Payment).filter(Payment.student_id == user.id).order_by(Payment.created_at.desc()).limit(10).all()
            if payments:
                total = sum(p.amount for p in payments)
                response = f"💰 <b>To'lovlar tarixi:</b>\n\n"
                response += f"💵 Jami to'langan: ${total:,.2f}\n"
                response += f"📊 To'lovlar soni: {len(payments)}\n\n"
                response += "<b>Oxirgi to'lovlar:</b>\n"
                for payment in payments[:5]:
                    response += f"   • {payment.created_at.strftime('%d.%m.%Y')}: ${payment.amount:,.2f} - {payment.payment_month}\n"
            else:
                response = "❌ Hali hech qanday to'lov amalga oshirilmagan."
            self.send_message(chat_id, response)
        
        elif text == "⭐️ Baholarim" or text == "/grades":
            response = "⭐️ <b>Sizning baholaringiz:</b>\n\n"
            
            # Calculate attendance statistics
            attendances = db.query(Attendance).join(Lesson).filter(
                Attendance.student_id == user.id
            ).all()
            
            if attendances:
                total = len(attendances)
                present = len([a for a in attendances if a.status.value == "present"])
                late = len([a for a in attendances if a.status.value == "late"])
                absent = len([a for a in attendances if a.status.value == "absent"])
                
                response += f"📊 <b>Davomat statistikasi:</b>\n"
                response += f"   ✅ Keldi: {present} ({present*100//total if total > 0 else 0}%)\n"
                response += f"   ⏰ Kechikdi: {late}\n"
                response += f"   ❌ Kelmadi: {absent}\n"
                response += f"   📊 Jami: {total} dars\n\n"
            else:
                response += "📊 Hozircha davomat ma'lumotlari mavjud emas.\n\n"
            
            response += "💡 Baholar va topshiriqlar tez orada qo'shiladi!"
            self.send_message(chat_id, response)
        
        elif text == "📝 Vazifalarim" or text == "/tasks":
            response = "📝 <b>Sizning vazifalaringiz:</b>\n\n"
            response += "Bu funksiya yaqinda qo'shiladi!\n\n"
            response += "📌 Yangi vazifalar qo'shilishi bilan sizga xabar beramiz."
            self.send_message(chat_id, response)
        
        elif text == "❓ Yordam" or text == "/help":
            response = """❓ <b>Yordam bo'limi</b>

📚 <b>Kurslarim</b> - Siz o'qiyotgan kurslar ro'yxati
📅 <b>Jadvalim</b> - Haftalik dars jadvalingiz
💰 <b>To'lovlarim</b> - To'lov tarixingiz
⭐️ <b>Baholarim</b> - Baholaringiz va davomat
📝 <b>Vazifalarim</b> - Uy vazifalari va topshiriqlar

<b>Bot haqida:</b>
Bu bot sizga kurs markazi haqida ma'lumotlarni olish va tezkor xabarlarni qabul qilish imkonini beradi.

Savollaringiz bo'lsa, kurs administratoriga murojaat qiling."""
            self.send_message(chat_id, response)
        
        else:
            # Show main menu with keyboard
            response = """🤖 <b>Asosiy menyu</b>

Quyidagi tugmalardan birini tanlang:

📚 Kurslarim - Sizning kurslaringiz
📅 Jadvalim - Dars jadvalingiz
💰 To'lovlarim - To'lovlar tarixi
⭐️ Baholarim - Baholaringiz
📝 Vazifalarim - Vazifalar ro'yxati
❓ Yordam - Yordam va ma'lumot"""
            
            # Send message with keyboard
            try:
                payload = {
                    "chat_id": chat_id,
                    "text": response,
                    "parse_mode": "HTML",
                    "reply_markup": json.dumps(self.get_main_keyboard())
                }
                requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            except Exception as e:
                print(f"Error sending menu: {e}")
    
    def process_update(self, update):
        """Process a single update"""
        try:
            # Update last_update_id
            update_id = update.get('update_id')
            if update_id:
                self.last_update_id = update_id
            
            # Check for message
            if 'message' in update:
                message = update['message']
                chat_id = str(message['chat']['id'])
                text = message.get('text', '')
                
                # Handle /start command
                if text and text.startswith('/start'):
                    parts = text.split()
                    
                    if len(parts) > 1:
                        token = parts[1]
                        db = SessionLocal()
                        try:
                            user = db.query(User).filter(
                                User.telegram_link_token == token,
                                User.telegram_link_expires_at > datetime.utcnow()
                            ).first()
                            
                            if user:
                                user.telegram_chat_id = chat_id
                                user.telegram_link_token = None
                                user.telegram_link_expires_at = None
                                db.commit()
                                
                                welcome_text = f"""✅ <b>Tabriklaymiz! {user.full_name}</b>

Sizning profilingiz muvaffaqiyatli ulandi!

👇 Quyidagi menyudan kerakli bo'limni tanlang:"""
                                
                                # Send with keyboard
                                payload = {
                                    "chat_id": chat_id,
                                    "text": welcome_text,
                                    "parse_mode": "HTML",
                                    "reply_markup": json.dumps(self.get_main_keyboard())
                                }
                                requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
                            else:
                                self.send_message(
                                    chat_id,
                                    "❌ <b>Xato!</b>\n\nHavola noto'g'ri yoki muddati o'tgan."
                                )
                        finally:
                            db.close()
                    else:
                        # Send welcome without keyboard (will show after connection)
                        self.send_message(
                            chat_id,
                            f"🤖 <b>Kurs Markazi Botiga Xush Kelibsiz!</b>\n\n"
                            f"Botdan foydalanish uchun profilingizni ulang:\n"
                            f"1️⃣ Veb-saytga kiring\n"
                            f"2️⃣ Profil sozlamalariga o'ting\n"
                            f"3️⃣ Telegramni ulash tugmasini bosing\n"
                            f"4️⃣ Hosil bo'lgan havolani bosing"
                        )
                else:
                    # Process regular messages
                    db = SessionLocal()
                    try:
                        self.process_message(db, chat_id, text)
                    finally:
                        db.close()
        except Exception as e:
            print(f"Error processing update: {e}")
    
    def run(self):
        """Main polling loop"""
        print(f"[telegram] Starting bot: @{self.bot_username}")
        print(f"[telegram] Bot is running. Send /start to @{self.bot_username} on Telegram")
        
        while self.running:
            try:
                updates = self.get_updates()
                for update in updates:
                    self.process_update(update)
            except Exception as e:
                print(f"Error in poller loop: {e}")
            
            time.sleep(1)
    
    def stop(self):
        """Stop the poller"""
        self.running = False


# Global poller instance
_poller_thread = None
_poller = None

def start_telegram_poller():
    """Start the Telegram poller in background"""
    global _poller_thread, _poller
    
    if not settings.TELEGRAM_USE_POLLING:
        print("[telegram] Polling is disabled")
        return False
    
    if not settings.TELEGRAM_BOT_TOKEN:
        print("[telegram] TELEGRAM_BOT_TOKEN is not set")
        return False
    
    if _poller_thread and _poller_thread.is_alive():
        print("[telegram] Poller already running")
        return True
    
    _poller = SimpleTelegramPoller()
    
    def run_poller():
        _poller.run()
    
    _poller_thread = threading.Thread(target=run_poller, daemon=True)
    _poller_thread.start()
    print("[telegram] Poller started")
    return True

def stop_telegram_poller():
    """Stop the Telegram poller"""
    global _poller
    if _poller:
        _poller.stop()
        print("[telegram] Poller stopped")
