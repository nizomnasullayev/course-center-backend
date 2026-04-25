# test_telegram_config.py
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("Telegram Configuration:")
print(f"Token: {os.getenv('TELEGRAM_BOT_TOKEN', 'NOT SET')[:20]}...")
print(f"Username: {os.getenv('TELEGRAM_BOT_USERNAME', 'NOT SET')}")
print(f"Webhook Secret: {os.getenv('TELEGRAM_WEBHOOK_SECRET', 'NOT SET')[:10]}...")
print(f"Use Polling: {os.getenv('TELEGRAM_USE_POLLING', 'false')}")

# Try to import settings
try:
    from app.config import settings
    print("\n✅ Settings imported successfully")
except Exception as e:
    print(f"\n❌ Error importing settings: {e}")