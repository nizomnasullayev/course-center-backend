# test_keyboard.py
import requests
import json

TOKEN = "YOUR_BOT_TOKEN"  # Replace with your actual token
CHAT_ID = "YOUR_CHAT_ID"  # Replace with your Telegram chat ID

keyboard = {
    "keyboard": [
        [{"text": "📚 Kurslarim"}, {"text": "📅 Jadvalim"}],
        [{"text": "💰 To'lovlarim"}, {"text": "⭐️ Baholarim"}],
        [{"text": "📝 Vazifalarim"}, {"text": "❓ Yordam"}]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

response = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={
        "chat_id": CHAT_ID,
        "text": "📱 Quyida menyu tugmalari:",
        "reply_markup": keyboard,
        "parse_mode": "HTML"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")