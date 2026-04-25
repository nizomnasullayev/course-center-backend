# test_direct_keyboard.py
import requests
import json

# Get your bot token from .env
from app.config import settings

TOKEN = settings.TELEGRAM_BOT_TOKEN

# First, get your chat ID (send a message to your bot first)
print("Getting updates...")
response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
if response.status_code == 200:
    data = response.json()
    if data.get('ok') and data.get('result'):
        chat_id = data['result'][0]['message']['chat']['id']
        print(f"✅ Found chat ID: {chat_id}")
        
        # Test sending keyboard
        keyboard = {
            "keyboard": [
                [{"text": "📚 Kurslarim"}, {"text": "📅 Jadvalim"}],
                [{"text": "💰 To'lovlarim"}, {"text": "⭐️ Baholarim"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        
        # Method 1: Send as json parameter
        print("\nMethod 1: Sending keyboard...")
        response1 = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "Test keyboard - Method 1",
                "reply_markup": keyboard,
                "parse_mode": "HTML"
            }
        )
        print(f"Status: {response1.status_code}")
        print(f"Response: {response1.json()}")
        
        # Method 2: Send as JSON string
        print("\nMethod 2: Sending as JSON string...")
        response2 = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "Test keyboard - Method 2",
                "reply_markup": json.dumps(keyboard),
                "parse_mode": "HTML"
            }
        )
        print(f"Status: {response2.status_code}")
        print(f"Response: {response2.json()}")
        
    else:
        print("❌ No updates found. Send a message to your bot first!")
else:
    print(f"❌ Error: {response.status_code}")