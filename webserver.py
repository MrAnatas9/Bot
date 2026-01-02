from flask import Flask, render_template_string
import os
import threading

app = Flask(__name__)

# HTML страница для проверки
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Clan Bot - Render</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            display: inline-block;
        }
        h1 {
            margin-bottom: 20px;
        }
        .status {
            background: rgba(255, 255, 255, 0.2);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Clan Bot</h1>
        <div class="status">
            <h2>✅ Бот работает!</h2>
            <p>Статус: Активен 24/7</p>
            <p>Хостинг: Render.com</p>
        </div>
        <p>Поддержка: @MrAnatas</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    def run_bot():
        from bot import main
        main()
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask
    app.run(host='0.0.0.0', port=10000)
