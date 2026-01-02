#!/usr/bin/env python3
import os
import sys
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Запуск бота для Render"""
    try:
        # Проверяем переменные окружения
        required_vars = ['BOT_TOKEN', 'ADMIN_ID', 'CLAN_LINK']
        for var in required_vars:
            if not os.getenv(var):
                logger.error(f"❌ Отсутствует переменная окружения: {var}")
                return
        
        # Импортируем и запускаем бота
        from bot import main as bot_main
        logger.info("🚀 Запускаем бота на Render...")
        bot_main()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
