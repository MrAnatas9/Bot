from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return "✅ Бот клана АД работает!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    print("🌐 Запускаем веб-сервер...")
    keep_alive()
    print("✅ Веб-сервер запущен!")
