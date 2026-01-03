import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from config import *
from database import *
from handlers import *

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== СОЗДАНИЕ И НАСТРОЙКА ПРИЛОЖЕНИЯ ==========
def setup_application() -> Application:
    """Создает и настраивает приложение"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ========== ОСНОВНЫЕ КОМАНДЫ ==========
    application.add_handler(CommandHandler("start", start_command))
    
    # ========== РЕГИСТРАЦИЯ ==========
    reg_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_registration, pattern='^register$')],
        states={
            ASKING_NICKNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_nickname)
            ],
            ASKING_SOURCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_source)
            ],
            SELECTING_JOBS: [
                CallbackQueryHandler(handle_callback, pattern='^cat_|^job_toggle_|^show_selected|^finish_selection|^back_to_categories|^confirm_selection')
            ],
            CONFIRM_REGISTRATION: [
                CallbackQueryHandler(handle_callback, pattern='^submit_registration|^back_to_categories')
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
        per_message=False
    )
    application.add_handler(reg_conv_handler)
    
    # ========== ПЕРЕВОДЫ ==========
    transfer_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_transfer, pattern='^transfer$')],
        states={
            TRANSFER_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_transfer)
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
        per_message=False
    )
    application.add_handler(transfer_conv_handler)
    
    # ========== ЗАДАНИЯ PROOF ==========
    proof_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern='^submit_proof_')],
        states={
            TASK_PROOF: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_task_proof)
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
        per_message=False
    )
    application.add_handler(proof_conv_handler)
    
    # ========== ГРУППОВЫЕ КОМАНДЫ ==========
    # Разрешаем команды только в группах (и личных сообщениях для отладки)
    application.add_handler(MessageHandler(
        filters.TEXT & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP), 
        handle_group_commands
    ))
    
    # ========== CALLBACK ОБРАБОТЧИК ==========
    # Основные callback-запросы
    application.add_handler(CallbackQueryHandler(handle_callback, pattern='^back$|^profile$|^tasks$|^show_selected$|^finish_selection$|^confirm_selection$|^back_to_categories$'))
    
    # Задания
    application.add_handler(CallbackQueryHandler(handle_callback, pattern='^take_task_'))
    
    return application

# ========== ФУНКЦИИ ДЛЯ РЕНДЕРА ==========
def keep_alive():
    """Функция для поддержания работы на Render"""
    import http.server
    import socketserver
    import threading
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Bot is alive!')
    
    def run_server():
        port = 8080
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Web server running on port {port}")
            httpd.serve_forever()
    
    # Запускаем веб-сервер в отдельном потоке
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

# ========== ЗАПУСК ПРОВЕРОК ==========
async def start_periodic_tasks(context: ContextTypes.DEFAULT_TYPE):
    """Запускает периодические задачи"""
    # Проверяем просроченные задания каждые 10 минут
    if context.job_queue:
        context.job_queue.run_repeating(
            lambda ctx: check_expired_tasks(),
            interval=600,  # 10 минут
            first=10
        )
        logger.info("Периодические задачи запущены")

# ========== ОСНОВНОЙ ЗАПУСК ==========
async def main():
    """Основная функция запуска"""
    logger.info("=" * 50)
    logger.info("🚀 ЗАПУСК БОТА КЛАНА АД")
    logger.info("=" * 50)
    
    # Проверяем конфигурацию
    logger.info(f"✅ Токен бота: {'установлен' if BOT_TOKEN else 'НЕ УСТАНОВЛЕН!'}")
    logger.info(f"✅ ID админа: {ADMIN_ID}")
    logger.info(f"✅ Supabase URL: {SUPABASE_URL[:30]}...")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен!")
        return
    
    # Инициализируем базу данных
    try:
        initialize_database()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы: {e}")
    
    # Создаем приложение
    application = setup_application()
    
    # Добавляем задачу при запуске
    application.job_queue.run_once(start_periodic_tasks, when=5)
    
    # Запускаем веб-сервер для Render (если нужно)
    if os.getenv("RENDER", False):
        keep_alive()
    
    # Запускаем бота
    logger.info("🤖 Бот запускается...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Ожидаем завершения
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
