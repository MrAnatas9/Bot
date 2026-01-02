import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6495178643"))
CLAN_LINK = os.getenv("CLAN_LINK", "https://t.me/+ytVpfVJ_5rk1ODQy")

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env файле!")
