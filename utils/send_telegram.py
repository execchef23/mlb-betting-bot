import requests

# Set your credentials here
BOT_TOKEN = "7495487516:AAHoMVJ6cInnwddunBbbiamvWuOdt71A0lo"
CHAT_ID = "6209381025"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"❌ Telegram error: {response.status_code} - {response.text}")
    else:
        print("✅ Telegram alert sent.")