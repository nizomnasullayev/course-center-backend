# test_bot_token.py
import requests
from app.config import settings

print("Testing bot token from .env file...")
print(f"Bot Token: {settings.TELEGRAM_BOT_TOKEN[:15]}...")

response = requests.get(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe")

if response.status_code == 200:
    data = response.json()
    if data.get('ok'):
        print(f"✅ Bot is working!")
        print(f"   Name: {data['result']['first_name']}")
        print(f"   Username: @{data['result']['username']}")
        print(f"   Bot ID: {data['result']['id']}")
        
        # Get your chat ID (you need to send a message to the bot first)
        updates = requests.get(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates")
        if updates.status_code == 200:
            updates_data = updates.json()
            if updates_data.get('ok') and updates_data.get('result'):
                chat_id = updates_data['result'][0]['message']['chat']['id']
                print(f"   Your Chat ID: {chat_id}")
            else:
                print("\n⚠️ Send a message to your bot first (any message), then run this script again")
    else:
        print(f"❌ Bot error: {data}")
else:
    print(f"❌ Cannot reach bot: HTTP {response.status_code}")