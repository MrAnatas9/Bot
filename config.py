import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6495178643"))
CLAN_LINK = os.getenv("CLAN_LINK", "https://t.me/+ytVpfVJ_5rk1ODQy")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://oomxbawrjmqczezdpaqp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_secret_yF3kBESRC2YLxW4427qUjQ_gs1hG5LD")

# Экономика
START_COINS = 25
MAX_DEBT = 500
CLAN_CREDIT_RATE = 1.10  # +10%
PLAYER_CREDIT_MIN_RATE = 1.05  # +5%
PLAYER_CREDIT_MAX_RATE = 1.20  # +20%

# Задания
TASK_DEADLINE_HOURS = 72  # 3 дня
TASK_PENALTY_PERCENT = 0.25  # 25% штраф за просрочку

# Уровни
EXP_PER_LEVEL = 100
LEVEL_UP_COINS = 50

# Работы
MAX_JOBS_PER_USER = 3

# Группы (для групповых команд)
GROUP_IDS = [-1001234567890]  # Замените на ID вашей группы

# Проверки
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен!")
