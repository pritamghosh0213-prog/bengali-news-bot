import requests
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

def fetch_top_news():
    """Fetch top 5 headlines from NewsAPI"""
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "category": "general",
        "pageSize": 5
    }
    response = requests.get(url, params=params)
    print("News API status:", response.status_code)
    data = response.json()
    articles = data.get("articles", [])
    headlines = []
    for article in articles:
        title = article.get("title", "")
        source = article.get("source", {}).get("name", "")
        if title and "[Removed]" not in title:
            headlines.append({"title": title, "source": source})
    return headlines

def translate_to_bengali(text):
    """Translate English text to Bengali using MyMemory (free, no key needed)"""
    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": text,
        "langpair": "en|bn"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        translated = data["responseData"]["translatedText"]
        print(f"Translated: {translated}")
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def send_telegram_message(text):
    """Send message to Telegram channel"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    r = requests.post(url, json=payload)
    print("Telegram status:", r.status_code)
    print("Telegram response:", r.text)
    return r.json()

def main():
    print("Starting Bengali News Bot...")
    today = datetime.now().strftime("%d %B %Y")

    headlines = fetch_top_news()
    if not headlines:
        print("No headlines found!")
        return

    message = f"🗞️ <b>আজকের শীর্ষ খবর</b>\n"
    message += f"📅 {today}\n"
    message += "━━━━━━━━━━━━━━━━\n\n"

    for i, item in enumerate(headlines, 1):
        bengali_title = translate_to_bengali(item["title"])
        source = item["source"]
        message += f"<b>{i}.</b> {bengali_title}\n"
        message += f"   📰 <i>{source}</i>\n\n"

    message += "━━━━━━━━━━━━━━━━\n"
    message += "🤖 <i>স্বয়ংক্রিয় খবর বট</i>"

    print("Final message:")
    print(message)

    result = send_telegram_message(message)
    if result.get("ok"):
        print("✅ News sent to Telegram successfully!")
    else:
        print("❌ Failed to send:", result)

main()
