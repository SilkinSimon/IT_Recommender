import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://svd-bot-api.duckdns.org")

if not BOT_TOKEN:
    raise ValueError("Токен бота не найден")