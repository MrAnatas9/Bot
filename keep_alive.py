#!/usr/bin/env python3
"""
Файл для поддержания активности бота на PythonAnywhere
"""
import time
import requests
import threading
import logging
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BotRunner:
    def __init__(self):
        self.bot_thread = None
        self.keep_alive_thread = None
        self.running = False
        
    def run_bot(self):
        """Запускает основного бота"""
        try:
            from bot import main
            logger.info("🚀 Запускаем основного бота...")
            main()
        except Exception as e:
            logger.error(f"❌ Ошибка бота: {e}")
            import traceback
            traceback.print_exc()
            
    def keep_alive_ping(self):
        """Пингует приложение чтобы оно не отключалось"""
        # URL вашего приложения на PythonAnywhere
        app_url = "https://ВАШ_ЛОГИН.pythonanywhere.com"
        
        while self.running:
            try:
                response = requests.get(app_url, timeout=10)
                logger.info(f"✅ Пинг отправлен: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Ошибка пинга: {e}")
            
            # Ждем 5 минут между пингами
            time.sleep(300)
    
    def start(self):
        """Запускает все компоненты"""
        self.running = True
        
        # Запускаем бота в отдельном потоке
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
        
        # Запускаем пинг для поддержания активности
        self.keep_alive_thread = threading.Thread(target=self.keep_alive_ping, daemon=True)
        self.keep_alive_thread.start()
        
        logger.info("✅ Все компоненты запущены")
        
        # Бесконечный цикл главного потока
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Останавливаем бота...")
            self.running = False
            if self.bot_thread:
                self.bot_thread.join(timeout=5)
            if self.keep_alive_thread:
                self.keep_alive_thread.join(timeout=5)

if __name__ == "__main__":
    runner = BotRunner()
    runner.start()
