
"""
Standalone Telegram Webhook Setup Script
This script doesn't depend on your app modules
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def setup_webhook():
    """Setup Telegram webhook"""
    
    # Read from .env directly
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    bot_username = os.getenv('TELEGRAM_BOT_USERNAME', '')
    webhook_secret = os.getenv('TELEGRAM_WEBHOOK_SECRET', '')
    app_base_url = os.getenv('APP_BASE_URL', 'https://yourdomain.com')
    use_polling = os.getenv('TELEGRAM_USE_POLLING', 'false')
    
    print("=" * 60)
    print("Telegram Webhook Setup")
    print("=" * 60)
    
    print(f"\n📋 Configuration from .env:")
    print(f"   Bot Token: {token[:15]}...{token[-5:] if len(token) > 20 else ''}")
    print(f"   Bot Username: @{bot_username}")
    print(f"   Webhook Secret: {webhook_secret[:10]}...")
    print(f"   Base URL: {app_base_url}")
    print(f"   Use Polling: {use_polling}")
    
    # Check if using polling
    if use_polling.lower() == 'true':
        print("\n⚠️  TELEGRAM_USE_POLLING is set to 'true'")
        print("   You don't need to set up a webhook when using polling mode.")
        print("   The bot will automatically fetch updates.")
        return True
    
    # Validate token
    if not token or token == 'your_actual_bot_token_here':
        print("\n❌ ERROR: TELEGRAM_BOT_TOKEN is not set in .env file")
        print("\nHow to get a bot token:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send /newbot and follow instructions")
        print("3. Copy the token you receive")
        return False
    
    # Construct webhook URL
    webhook_url = f"{app_base_url}/telegram-webhook/{webhook_secret}"
    
    print(f"\n🔗 Webhook URL: {webhook_url}")
    
    # Check if using default domain
    if 'yourdomain.com' in app_base_url:
        print("\n⚠️  WARNING: Using default domain 'yourdomain.com'")
        print("\n📡 For local development, you need a public HTTPS URL:")
        print("   1. Install ngrok from https://ngrok.com")
        print("   2. Run: ngrok http 8000")
        print("   3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)")
        print("   4. Update APP_BASE_URL in .env file")
        print("\n   Example: APP_BASE_URL=https://abc123.ngrok.io")
        
        response = input("\nContinue with setup anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    # Set webhook
    print("\n📡 Setting webhook...")
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            json={"url": webhook_url}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook set successfully!")
                
                # Get webhook info
                info_response = requests.get(
                    f"https://api.telegram.org/bot{token}/getWebhookInfo"
                )
                if info_response.status_code == 200:
                    info = info_response.json()
                    result_info = info.get('result', {})
                    print("\n📊 Current Webhook Status:")
                    print(f"   URL: {result_info.get('url', 'Not set')}")
                    print(f"   Pending updates: {result_info.get('pending_update_count', 0)}")
                    print(f"   Last error: {result_info.get('last_error_message', 'None')}")
                
                print("\n✨ Next steps:")
                print(f"   1. Make sure your FastAPI app is running")
                print(f"   2. Visit: {webhook_url.replace(webhook_secret, 'YOUR_SECRET')}")
                print(f"   3. Test by messaging @{bot_username}")
                
                return True
            else:
                print(f"❌ Telegram API error: {result}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def delete_webhook():
    """Delete current webhook"""
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    response = requests.post(f"https://api.telegram.org/bot{token}/deleteWebhook")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            print("✅ Webhook deleted successfully")
        else:
            print(f"❌ Failed: {result}")
    else:
        print(f"❌ HTTP error: {response.status_code}")

def get_webhook_info():
    """Get current webhook information"""
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    response = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
    
    if response.status_code == 200:
        info = response.json()
        print("\n📡 Current Webhook Configuration:")
        print("=" * 50)
        result = info.get('result', {})
        print(f"URL: {result.get('url', 'Not set')}")
        print(f"Pending updates: {result.get('pending_update_count', 0)}")
        print(f"Last error: {result.get('last_error_message', 'None')}")
        print(f"Last error date: {result.get('last_error_date', 'N/A')}")
    else:
        print(f"❌ Failed to get webhook info: {response.status_code}")

def test_bot():
    """Test if bot is working"""
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    bot_username = os.getenv('TELEGRAM_BOT_USERNAME', '')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    print(f"\n🤖 Testing bot @{bot_username}...")
    
    # Get bot info
    response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            bot_info = result.get('result', {})
            print(f"✅ Bot is active!")
            print(f"   Name: {bot_info.get('first_name')}")
            print(f"   Username: @{bot_info.get('username')}")
            print(f"   ID: {bot_info.get('id')}")
            return True
        else:
            print(f"❌ Bot error: {result}")
            return False
    else:
        print(f"❌ Cannot reach bot: HTTP {response.status_code}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram Bot Webhook Manager')
    parser.add_argument('action', nargs='?', default='test',
                       choices=['test', 'setup', 'info', 'delete'],
                       help='Action to perform (default: test)')
    
    args = parser.parse_args()
    
    if args.action == 'test':
        test_bot()
    elif args.action == 'setup':
        setup_webhook()
    elif args.action == 'info':
        get_webhook_info()
    elif args.action == 'delete':
        delete_webhook()