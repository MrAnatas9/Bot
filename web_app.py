#!/usr/bin/env python3
"""
Веб-приложение для PythonAnywhere
"""
from flask import Flask, render_template_string
import threading
import logging
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# HTML шаблон для страницы
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Clan Bot - PythonAnywhere</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-top: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .status {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            font-size: 1.2em;
        }
        .status.running {
            border-left: 5px solid #4CAF50;
        }
        .info-box {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
        }
        h2 {
            color: #FFD700;
            margin-top: 0;
        }
        ul {
            padding-left: 20px;
        }
        li {
            margin: 10px 0;
            font-size: 1.1em;
        }
        .emoji {
            font-size: 1.3em;
            margin-right: 10px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 0.9em;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Clan Bot Management</h1>
        
        <div class="status running">
            <span class="emoji">✅</span>
            <strong>Бот активен и работает 24/7</strong>
        </div>
        
        <div class="info-box">
            <h2>📊 Информация о системе:</h2>
            <ul>
                <li><span class="emoji">🖥️</span> Хостинг: PythonAnywhere</li>
                <li><span class="emoji">⚡</span> Статус: Работает постоянно</li>
                <li><span class="emoji">🔄</span> Авто-перезапуск: Включен</li>
                <li><span class="emoji">📈</span> Uptime: 100%</li>
            </ul>
        </div>
        
        <div class="info-box">
            <h2>🔧 Функции бота:</h2>
            <ul>
                <li><span class="emoji">👥</span> Управление кланом</li>
                <li><span class="emoji">💼</span> Система работ</li>
                <li><span class="emoji">💰</span> Экономика акойнов</li>
                <li><span class="emoji">📋</span> Задания и квесты</li>
                <li><span class="emoji">👑</span> Админ панель</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Bot is running on PythonAnywhere | Last updated: {{ timestamp }}</p>
            <p>Для связи: @MrAnatas</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Главная страница"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template_string(HTML_TEMPLATE, timestamp=timestamp)

@app.route('/health')
def health_check():
    """Проверка здоровья для пингов"""
    return "OK", 200

@app.route('/start_bot')
def start_bot():
    """Запуск бота через веб-интерфейс"""
    try:
        # Запускаем бота в отдельном потоке
        def run_bot():
            from bot import main
            main()
        
        thread = threading.Thread(target=run_bot, daemon=True)
        thread.start()
        
        return "Bot started successfully!", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    # Эта часть только для локального тестирования
    app.run(debug=True)
else:
    # На PythonAnywhere это будет вызвано через WSGI
    print("✅ Веб-приложение загружено и готово к работе")
