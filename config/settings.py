"""
Настройки приложения
"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "subito_parser_bot")

# Parser
PARSE_INTERVAL = int(os.getenv("PARSE_INTERVAL", "300"))  # 5 минут по умолчанию
MAX_CONCURRENT_PARSERS = int(os.getenv("MAX_CONCURRENT_PARSERS", "30"))

# Subscription plans (в часах)
SUBSCRIPTION_PLANS = {
    "1h": 1,
    "24h": 24,
    "48h": 48
}

# Subito.it settings
SUBITO_BASE_URL = "https://www.subito.it"
SUBITO_SEARCH_URL = f"{SUBITO_BASE_URL}/annunci-italia/vendita/usato/"

