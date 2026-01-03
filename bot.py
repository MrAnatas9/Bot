import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from config import BOT_TOKEN, ADMIN_ID, CLAN_LINK
from database_supabase import (
    users, applications, messages_to_admin, tasks,
    save_user, get_user, get_all_users, save_application, get_application, 
    approve_application, reject_application, update_user_nickname, update_user_jobs,
    ban_user, unban_user, add_coins, add_exp, create_task, get_active_tasks,
    assign_task, complete_task, save_message_to_admin, get_messages_to_admin,
    get_message, update_message_status, JOBS_DETAILS, get_jobs_by_category,
    get_categories, is_job_available, get_users_count_by_job
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

 # Состояния
(
    ASKING_NICKNAME, ASKING_SOURCE, SELECTING_JOBS, 
    CONFIRM_REGISTRATION, CHANGING_NICKNAME, SENDING_MESSAGE,
    CREATING_TASK_TITLE, CREATING_TASK_DESC, CREATING_TASK_REWARD_COINS, 
    CREATING_TASK_REWARD_EXP, BAN_REASON, MESSAGE_REASON,
    GIVING_COINS, CHANGING_JOBS, VIEWING_APPS, VIEWING_MSGS,
    VIEWING_USERS
) = range(17)

# Функция для главного меню
def get_main_menu(user_id):
    """Возвращает главное меню в зависимости от пользователя"""
    user = get_user(user_id)
    
    if user_id == ADMIN_ID:
        # Меню админа
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("📝 Заявки", callback_data="applications")],
            [InlineKeyboardButton("📋 Задания", callback_data="admin_tasks")],
            [InlineKeyboardButton("👥 Пользователи", callback_data="users_list")],
            [InlineKeyboardButton("💌 Сообщения", callback_data="admin_messages")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings")]
        ]
    elif user:
        # Меню обычного пользователя
        keyboard = [
            [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
            [InlineKeyboardButton("📋 Задания", callback_data="tasks")],
            [InlineKeyboardButton("💼 Мои работы", callback_data="my_jobs")],
            [InlineKeyboardButton("🏆 Топ игроков", callback_data="top")],
            [InlineKeyboardButton("✉️ Отправить сообщение", callback_data="send_message")],
            [
                InlineKeyboardButton("🔄 Сменить ник", callback_data="change_nick"),
                InlineKeyboardButton("🔄 Сменить работы", callback_data="change_jobs")
            ],
            [InlineKeyboardButton("📞 Поддержка", url="https://t.me/MrAnatas")]
        ]
    else:
        # Меню для незарегистрированных
        keyboard = [
            [InlineKeyboardButton("🚀 Регистрация", callback_data="register")],
            [InlineKeyboardButton("📞 Поддержка", url="https://t.me/MrAnatas")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

# ========== ОСНОВНЫЕ ФУНКЦИИ ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    
    if update.message:
        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n"
            f"👹 Добро пожаловать в бот клана АД!\n\n"
            f"Выберите действие:",
            reply_markup=get_main_menu(user.id)
        )
    else:
        await update.callback_query.edit_message_text(
            f"👋 Привет, {user.first_name}!\n"
            f"👹 Добро пожаловать в бот клана АД!\n\n"
            f"Выберите действие:",
            reply_markup=get_main_menu(user.id)
        )

# ========== РЕГИСТРАЦИЯ ==========

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает регистрацию"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    if get_user(user.id):
        await query.edit_message_text(
            "✅ Вы уже зарегистрированы!",
            reply_markup=get_main_menu(user.id)
        )
        return
    
    await query.edit_message_text(
        "📝 **РЕГИСТРАЦИЯ В КЛАНЕ**\n\n"
        "Введите ваш игровой никнейм:"
    )
    
    context.user_data['selected_jobs'] = []
    return ASKING_NICKNAME

async def ask_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает никнейм"""
    nickname = update.message.text.strip()
    
    if len(nickname) < 3:
        await update.message.reply_text("❌ Никнейм должен быть не менее 3 символов.\nПопробуйте снова:")
        return ASKING_NICKNAME
    
    context.user_data['nickname'] = nickname
    await update.message.reply_text(
        "📌 **Откуда вы узнали о клане?**"
    )
    
    return ASKING_SOURCE

async def ask_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает источник"""
    source = update.message.text.strip()
    context.user_data['source'] = source
    
    # Показываем категории работ
    categories = get_categories()
    keyboard = []
    for category in categories:
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    
    await update.message.reply_text(
        "💼 **ВЫБОР РАБОТ**\n\n"
        "Вы можете выбрать до 3 работ.\n"
        "Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return SELECTING_JOBS

async def show_category_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE, category):
    """Показывает работы в категории"""
    query = update.callback_query
    await query.answer()
    
    jobs = get_jobs_by_category(category)
    
    text = f"💼 **{category}**\n\n"
    text += "Выберите работу (можно до 3):\n\n"
    
    keyboard = []
    for job_name, job_details in jobs.items():
        available = is_job_available(job_name)
        current_count = get_users_count_by_job(job_name)
        max_count = job_details['max_users']
        
        status = "✅" if available else "❌"
        availability = f"({current_count}/{max_count})"
        
        if job_name in context.user_data.get('selected_jobs', []):
            text += f"✓ {job_name} {availability}\n"
            text += f"   📝 {job_details['description']}\n"
            text += f"   👑 Ур. {job_details['min_level']}+\n\n"
        else:
            text += f"{status} {job_name} {availability}\n"
            text += f"   📝 {job_details['description']}\n"
            text += f"   👑 Ур. {job_details['min_level']}+\n\n"
        
        # Кнопка для добавления/удаления работы
        if job_name in context.user_data.get('selected_jobs', []):
            keyboard.append([InlineKeyboardButton(f"❌ Убрать {job_name}", callback_data=f"job_toggle_{job_name}")])
        elif available and len(context.user_data.get('selected_jobs', [])) < 3:
            keyboard.append([InlineKeyboardButton(f"✅ Выбрать {job_name}", callback_data=f"job_toggle_{job_name}")])
        else:
            if not available:
                keyboard.append([InlineKeyboardButton(f"❌ {job_name} (нет мест)", callback_data="no_action")])
            elif len(context.user_data.get('selected_jobs', [])) >= 3:
                keyboard.append([InlineKeyboardButton(f"❌ {job_name} (лимит 3)", callback_data="no_action")])
    
    keyboard.append([InlineKeyboardButton("📋 Мои выбранные работы", callback_data="show_selected")])
    keyboard.append([InlineKeyboardButton("✅ Завершить выбор", callback_data="finish_selection")])
    keyboard.append([InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_categories")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def toggle_job_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, job_name):
    """Добавляет или убирает работу из выбранных"""
    query = update.callback_query
    await query.answer()
    
    selected_jobs = context.user_data.get('selected_jobs', [])
    
    if job_name in selected_jobs:
        selected_jobs.remove(job_name)
        await query.answer(f"❌ {job_name} удалена из выбранных")
    else:
        if len(selected_jobs) >= 3:
            await query.answer("❌ Можно выбрать максимум 3 работы!")
            return
        
        # Проверяем доступность работы
        if not is_job_available(job_name):
            await query.answer("❌ Эта работа уже занята!")
            return
        
        selected_jobs.append(job_name)
        await query.answer(f"✅ {job_name} добавлена в выбранные")
    
    context.user_data['selected_jobs'] = selected_jobs
    
    # Получаем категорию работы для возврата
    job_details = JOBS_DETAILS.get(job_name)
    if job_details:
        await show_category_jobs(update, context, job_details['category'])

async def show_selected_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает выбранные работы"""
    query = update.callback_query
    await query.answer()
    
    selected_jobs = context.user_data.get('selected_jobs', [])
    
    if not selected_jobs:
        await query.edit_message_text(
            "❌ Вы не выбрали ни одной работы!\n\n"
            "Пожалуйста, выберите хотя бы одну работу.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")]
            ])
        )
        return
    
    text = "📋 **ВАШИ ВЫБРАННЫЕ РАБОТЫ:**\n\n"
    for i, job_name in enumerate(selected_jobs, 1):
        job_details = JOBS_DETAILS.get(job_name, {})
        text += f"{i}. {job_name}\n"
        text += f"   📝 {job_details.get('description', 'Нет описания')}\n"
        text += f"   👑 Ур. {job_details.get('min_level', 1)}+\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Изменить выбор", callback_data="back_to_categories")],
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_selection")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def confirm_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждает выбор работ"""
    query = update.callback_query
    await query.answer()
    
    selected_jobs = context.user_data.get('selected_jobs', [])
    
    if not selected_jobs:
        await query.edit_message_text(
            "❌ Вы не выбрали ни одной работы!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")]
            ])
        )
        return
    
    # Показываем подтверждение
    text = "📋 **ПОДТВЕРЖДЕНИЕ РЕГИСТРАЦИИ**\n\n"
    text += f"👤 **Никнейм:** {context.user_data['nickname']}\n"
    text += f"📌 **Источник:** {context.user_data['source']}\n\n"
    text += "💼 **Выбранные работы:**\n"
    
    for job_name in selected_jobs:
        text += f"• {job_name}\n"
    
    text += f"\nВсего выбрано работ: {len(selected_jobs)}/3\n\n"
    text += "Всё верно?"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, отправить", callback_data="submit_registration"),
            InlineKeyboardButton("❌ Нет, изменить", callback_data="back_to_categories")
        ]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CONFIRM_REGISTRATION

async def submit_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет заявку на регистрацию"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    selected_jobs = context.user_data.get('selected_jobs', [])
    
    # Сохраняем заявку
    app_id = save_application(
        user.id,
        user.username,
        context.user_data['nickname'],
        context.user_data['source'],
        selected_jobs
    )
    
    # Отправляем админу
    await send_application_to_admin(context, app_id)
    
    await query.edit_message_text(
        f"✅ **ЗАЯВКА ОТПРАВЛЕНА!**\n\n"
        f"📋 **ID заявки:** #{app_id}\n"
        f"👤 **Ваш никнейм:** {context.user_data['nickname']}\n"
        f"💼 **Выбранные работы:** {len(selected_jobs)}\n\n"
        f"Ожидайте решения администратора.\n"
        f"📞 Поддержка: @MrAnatas\n\n"
        f"🔗 Ссылка на чат клана будет отправлена после одобрения.",
        reply_markup=get_main_menu(user.id)
    )
    
    # Очищаем данные
    context.user_data.clear()
    
    return ConversationHandler.END

async def send_application_to_admin(context, app_id):
    """Отправляет заявку админу"""
    app = get_application(app_id)
    
    if not app:
        return
    
    text = (
        f"📨 **НОВАЯ ЗАЯВКА #{app_id}**\n\n"
        f"👤 **ID:** {app['user_id']}\n"
        f"📱 **Юзернейм:** @{app.get('username', 'нет')}\n"
        f"🎮 **Никнейм:** {app['nickname']}\n"
        f"📌 **Источник:** {app['source']}\n\n"
        f"💼 **Выбранные работы ({len(app['selected_jobs'])}):**\n"
    )
    
    for job in app['selected_jobs']:
        text += f"• {job}\n"
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{app_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{app_id}")
        ],
        [InlineKeyboardButton("💬 Написать сообщение", callback_data=f"message_{app_id}")]
    ])
    
    try:
        await context.bot.send_message(ADMIN_ID, text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка отправки админу: {e}")

# ========== ПРОФИЛЬ И РАБОТЫ ==========

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает профиль"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user:
        await query.edit_message_text(
            "❌ Вы не зарегистрированы!",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    text = (
        f"👤 **ПРОФИЛЬ ИГРОКА**\n\n"
        f"🎮 **Никнейм:** {user['nickname']}\n"
        f"📱 **Телеграм:** @{user.get('username', 'нет')}\n"
        f"👑 **Уровень:** {user['level']}\n"
        f"📈 **Опыт:** {user['exp']}/{user['level'] * 100}\n"
        f"💰 **Акойны:** {user['coins']} 🪙\n"
        f"💌 **Сообщений отправлено:** {user.get('messages_sent', 0)}\n"
        f"📅 **Регистрация:** {user.get('registration_date', '2026-01-02')}\n"
        f"🆔 **ID:** {user['user_id']}"
    )
    
    if user.get('is_admin'):
        text += "\n\n👑 **Статус: Администратор**"
    
    await query.edit_message_text(
        text,
        reply_markup=get_main_menu(user_id)
    )

async def show_my_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает работы пользователя"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user:
        await query.edit_message_text(
            "❌ Вы не зарегистрированы!",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    selected_jobs = user.get('selected_jobs', [])
    
    if not selected_jobs:
        text = "💼 **ВЫ НЕ ИМЕЕТЕ РАБОТ**\n\n"
        text += "Используйте 'Сменить работы' чтобы выбрать работы."
    else:
        text = f"💼 **ВАШИ РАБОТЫ** ({len(selected_jobs)}/3)\n\n"
        
        for i, job_name in enumerate(selected_jobs, 1):
            job_details = JOBS_DETAILS.get(job_name, {})
            current_count = get_users_count_by_job(job_name)
            max_count = job_details.get('max_users', 1)
            
            text += f"{i}. **{job_name}**\n"
            text += f"   📝 {job_details.get('description', 'Нет описания')}\n"
            text += f"   👑 Ур. {job_details.get('min_level', 1)}+\n"
            text += f"   👥 {current_count}/{max_count} мест\n"
            
            if i == 1:
                text += f"   ⭐ **Основная работа**\n"
            
            text += "\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Сменить работы", callback_data="change_jobs")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== СМЕНА НИКА И РАБОТ ==========

async def change_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает смену ника"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user:
        await query.edit_message_text(
            "❌ Вы не зарегистрированы!",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    await query.edit_message_text(
        f"🔄 **СМЕНА НИКНЕЙМА**\n\n"
        f"Текущий никнейм: {user['nickname']}\n\n"
        f"Введите новый никнейм:"
    )
    
    return CHANGING_NICKNAME

async def process_new_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает новый никнейм"""
    new_nickname = update.message.text.strip()
    user_id = update.effective_user.id
    
    if len(new_nickname) < 3:
        await update.message.reply_text(
            "❌ Никнейм должен быть не менее 3 символов.\n"
            "Попробуйте снова:"
        )
        return CHANGING_NICKNAME
    
    if update_user_nickname(user_id, new_nickname):
        await update.message.reply_text(
            f"✅ **НИКНЕЙМ ИЗМЕНЕН!**\n\n"
            f"Новый никнейм: {new_nickname}",
            reply_markup=get_main_menu(user_id)
        )
    else:
        await update.message.reply_text(
            "❌ Ошибка при изменении никнейма!",
            reply_markup=get_main_menu(user_id)
        )
    
    return ConversationHandler.END

async def change_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает смену работ"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user:
        await query.edit_message_text(
            "❌ Вы не зарегистрированы!",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    # Загружаем текущие работы
    context.user_data['selected_jobs'] = user.get('selected_jobs', []).copy()
    context.user_data['changing_jobs'] = True
    
    # Показываем категории
    categories = get_categories()
    keyboard = []
    for category in categories:
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    
    await query.edit_message_text(
        "🔄 **СМЕНА РАБОТ**\n\n"
        "Вы можете выбрать до 3 работ.\n"
        "Текущие работы сохранены.\n"
        "Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CHANGING_JOBS

async def save_new_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет новые работы"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    selected_jobs = context.user_data.get('selected_jobs', [])
    
    if not selected_jobs:
        await query.edit_message_text(
            "❌ Вы не выбрали ни одной работы!",
            reply_markup=get_main_menu(user_id)
        )
        return ConversationHandler.END
    
    if update_user_jobs(user_id, selected_jobs):
        await query.edit_message_text(
            f"✅ **РАБОТЫ ОБНОВЛЕНЫ!**\n\n"
            f"Теперь у вас {len(selected_jobs)} работ.",
            reply_markup=get_main_menu(user_id)
        )
        
        # Уведомляем админа
        try:
            user = get_user(user_id)
            text = (
                f"🔄 **ПОЛЬЗОВАТЕЛЬ СМЕНИЛ РАБОТЫ**\n\n"
                f"👤 {user['nickname']} (@{user.get('username', 'нет')})\n"
                f"🆔 ID: {user_id}\n\n"
                f"💼 **Новые работы ({len(selected_jobs)}):**\n"
            )
            
            for job in selected_jobs:
                text += f"• {job}\n"
            
            await context.bot.send_message(ADMIN_ID, text)
        except Exception as e:
            logger.error(f"Ошибка уведомления админа: {e}")
        
    else:
        await query.edit_message_text(
            "❌ Ошибка при обновлении работ!",
            reply_markup=get_main_menu(user_id)
        )
    
    # Очищаем данные
    if 'changing_jobs' in context.user_data:
        del context.user_data['changing_jobs']
    
    return ConversationHandler.END

# ========== СООБЩЕНИЯ АДМИНУ ==========

async def send_message_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню отправки сообщений админу"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user:
        await query.edit_message_text(
            "❌ Вы не зарегистрированы!",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("💰 Запрос премии", callback_data="msg_premium")],
        [InlineKeyboardButton("💼 Запрос смены работы", callback_data="msg_job_change")],
        [InlineKeyboardButton("📝 Другое сообщение", callback_data="msg_other")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    
    await query.edit_message_text(
        "✉️ **ОТПРАВКА СООБЩЕНИЯ АДМИНИСТРАТОРУ**\n\n"
        "Выберите тип сообщения:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE, msg_type):
    """Начинает отправку сообщения"""
    query = update.callback_query
    await query.answer()
    
    msg_types = {
        "premium": "💰 ЗАПРОС ПРЕМИИ",
        "job_change": "💼 ЗАПРОС СМЕНЫ РАБОТЫ", 
        "other": "📝 ДРУГОЕ СООБЩЕНИЕ"
    }
    
    context.user_data['msg_type'] = msg_type
    
    await query.edit_message_text(
        f"✉️ **{msg_types[msg_type]}**\n\n"
        f"Напишите ваше сообщение администратору:"
    )
    
    return SENDING_MESSAGE

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщение для админа"""
    message_text = update.message.text.strip()
    user_id = update.effective_user.id
    msg_type = context.user_data.get('msg_type', 'other')
    
    if not message_text:
        await update.message.reply_text(
            "❌ Сообщение не может быть пустым!\n"
            "Попробуйте снова:"
        )
        return SENDING_MESSAGE
    
    # Сохраняем сообщение
    msg_id = save_message_to_admin(user_id, msg_type, message_text)
    
    # Отправляем админу
    user = get_user(user_id)
    msg_types_text = {
        "premium": "💰 Запрос премии",
        "job_change": "💼 Запрос смены работы",
        "other": "📝 Сообщение"
    }
    
    admin_text = (
        f"✉️ **НОВОЕ СООБЩЕНИЕ #{msg_id}**\n\n"
        f"📋 **Тип:** {msg_types_text[msg_type]}\n"
        f"👤 **От:** {user['nickname']} (@{user.get('username', 'нет')})\n"
        f"🆔 **ID:** {user_id}\n\n"
        f"📝 **Сообщение:**\n{message_text}"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Одобрить", callback_data=f"msg_approve_{msg_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"msg_reject_{msg_id}")
        ]
    ])
    
    try:
        await context.bot.send_message(ADMIN_ID, admin_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка отправки админу: {e}")
    
    await update.message.reply_text(
        f"✅ **СООБЩЕНИЕ ОТПРАВЛЕНО!**\n\n"
        f"📋 ID сообщения: #{msg_id}\n"
        f"📝 Тип: {msg_types_text[msg_type]}\n\n"
        f"Администратор рассмотрит ваше сообщение в ближайшее время.",
        reply_markup=get_main_menu(user_id)
    )
    
    # Очищаем данные
    if 'msg_type' in context.user_data:
        del context.user_data['msg_type']
    
    return ConversationHandler.END

# ========== ЗАДАНИЯ ==========

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает задания для пользователя"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user:
        await query.edit_message_text(
            "❌ Вы не зарегистрированы!",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    active_tasks = get_active_tasks()
    
    if not active_tasks:
        await query.edit_message_text(
            "📭 **Нет активных заданий**\n\n"
            "Задания создает администратор. Следите за обновлениями!",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    text = "📋 **ДОСТУПНЫЕ ЗАДАНИЯ**\n\n"
    
    for task in active_tasks[:5]:
        text += f"📌 **{task['title']}**\n"
        text += f"📝 {task['description']}\n"
        text += f"🎁 Награда: {task['reward_coins']}🪙 + {task['reward_exp']} опыта\n\n"
    
    if len(active_tasks) > 5:
        text += f"... и еще {len(active_tasks) - 5} заданий\n\n"
    
    text += "Для взятия задания свяжитесь с администратором."
    
    await query.edit_message_text(
        text,
        reply_markup=get_main_menu(user_id)
    )

# ========== ТОП ИГРОКОВ ==========

async def show_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает топ игроков"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    all_users = get_all_users()
    
    if not all_users:
        await query.edit_message_text(
            "🏆 **ТОП ИГРОКОВ**\n\n"
            "Пока никто не зарегистрирован!",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    # Сортируем по акойнам
    sorted_users = sorted(all_users, key=lambda x: x['coins'], reverse=True)
    
    text = "🏆 **ТОП ИГРОКОВ ПО АКОЙНАМ**\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(sorted_users[:10], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} **{user['nickname']}**\n"
        text += f"   💰 {user['coins']}🪙 | 👑 Ур. {user['level']}\n"
        text += f"   💼 {user['job']}\n\n"
    
    # Позиция текущего пользователя
    if user_id != ADMIN_ID:
        current_user = get_user(user_id)
        if current_user:
            position = next((i+1 for i, u in enumerate(sorted_users) if u['user_id'] == user_id), None)
            if position:
                text += f"📊 **Ваша позиция:** #{position}\n"
                text += f"💰 **Ваши акойны:** {current_user['coins']}🪙"
    
    await query.edit_message_text(
        text,
        reply_markup=get_main_menu(user_id)
    )

# ========== АДМИН ПАНЕЛЬ ==========

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика для админа"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ Нет доступа!")
        return
    
    all_users = get_all_users()
    pending_apps = [a for a in applications.values() if a['status'] == 'pending']
    pending_msgs = [m for m in messages_to_admin.values() if m['status'] == 'pending']
    active_tasks = get_active_tasks()
    
    total_coins = sum(u['coins'] for u in all_users)
    total_exp = sum(u['exp'] for u in all_users)
    
    # Самые популярные работы
    jobs_popularity = {}
    for user in all_users:
        for job in user.get('selected_jobs', []):
            jobs_popularity[job] = jobs_popularity.get(job, 0) + 1
    
    top_jobs = sorted(jobs_popularity.items(), key=lambda x: x[1], reverse=True)[:3]
    
    text = (
        f"📊 **СТАТИСТИКА КЛАНА**\n\n"
        f"👥 **Пользователей:** {len(all_users)}\n"
        f"💰 **Всего акойнов:** {total_coins} 🪙\n"
        f"📈 **Всего опыта:** {total_exp}\n"
        f"📝 **Ожидающих заявок:** {len(pending_apps)}\n"
        f"✉️ **Сообщений на рассмотрении:** {len(pending_msgs)}\n"
        f"📋 **Активных заданий:** {len(active_tasks)}\n\n"
        f"💼 **Популярные работы:**\n"
    )
    
    for job, count in top_jobs:
        text += f"• {job}: {count} чел.\n"
    
    await query.edit_message_text(
        text,
        reply_markup=get_main_menu(ADMIN_ID)
    )

async def admin_applications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Заявки для админа"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ Нет доступа!")
        return
    
    pending_apps = [a for a in applications.values() if a['status'] == 'pending']
    
    if not pending_apps:
        await query.edit_message_text(
            "📭 **Нет ожидающих заявок**",
            reply_markup=get_main_menu(ADMIN_ID)
        )
        return
    
    text = f"📝 **ЗАЯВКИ НА РЕГИСТРАЦИЮ** ({len(pending_apps)})\n\n"
    
    for i, app in enumerate(pending_apps[:5], 1):
        text += f"{i}. **#{app['id']}** - {app['nickname']}\n"
        text += f"   📱 @{app.get('username', 'нет')}\n"
        text += f"   💼 Работ: {len(app['selected_jobs'])}\n\n"
    
    if len(pending_apps) > 5:
        text += f"... и еще {len(pending_apps) - 5} заявок\n\n"
    
    keyboard = []
    for app in pending_apps[:3]:
        keyboard.append([
            InlineKeyboardButton(f"#{app['id']} {app['nickname'][:15]}", callback_data=f"view_app_{app['id']}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def view_application_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, app_id):
    """Просмотр заявки админом"""
    query = update.callback_query
    await query.answer()
    
    app = get_application(app_id)
    if not app:
        await query.edit_message_text("❌ Заявка не найдена!")
        return
    
    text = (
        f"📋 **ЗАЯВКА #{app_id}**\n\n"
        f"👤 **ID:** {app['user_id']}\n"
        f"📱 **Юзернейм:** @{app.get('username', 'нет')}\n"
        f"🎮 **Никнейм:** {app['nickname']}\n"
        f"📌 **Источник:** {app['source']}\n\n"
        f"💼 **Выбранные работы ({len(app['selected_jobs'])}):**\n"
    )
    
    for job in app['selected_jobs']:
        job_details = JOBS_DETAILS.get(job, {})
        current_count = get_users_count_by_job(job)
        max_count = job_details.get('max_users', 1)
        available = current_count < max_count
        
        status = "✅" if available else "❌"
        text += f"{status} {job} ({current_count}/{max_count})\n"
    
    text += f"\n📊 **Статус:** {app['status']}"
    
    if app['status'] == 'pending':
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"do_approve_{app_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"do_reject_{app_id}")
            ],
            [InlineKeyboardButton("💬 Написать сообщение", callback_data=f"admin_msg_{app_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="applications")]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="applications")]
        ])
    
    await query.edit_message_text(text, reply_markup=keyboard)

async def handle_approve_application(update: Update, context: ContextTypes.DEFAULT_TYPE, app_id):
    """Одобряет заявку"""
    query = update.callback_query
    await query.answer()
    
    if approve_application(app_id):
        app = get_application(app_id)
        
        # Отправляем приглашение пользователю
        try:
            await context.bot.send_message(
                app['user_id'],
                f"🎉 **ВАША ЗАЯВКА #{app_id} ОДОБРЕНА!**\n\n"
                f"👹 Добро пожаловать в клан АД!\n\n"
                f"👤 **Ваш никнейм:** {app['nickname']}\n"
                f"💼 **Основная работа:** {app['selected_jobs'][0] if app['selected_jobs'] else 'Нет'}\n"
                f"💰 **Начальные акойны:** 100 🪙\n"
                f"👑 **Уровень:** 1\n\n"
                f"🔗 **Ссылка на чат клана:** {CLAN_LINK}\n\n"
                f"📞 **Поддержка:** @MrAnatas\n\n"
                f"Слава Аду! 👹"
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления: {e}")
        
        await query.edit_message_text(
            f"✅ **ЗАЯВКА #{app_id} ОДОБРЕНА!**\n\n"
            f"👤 Пользователь: {app['nickname']}\n"
            f"🔗 Ссылка отправлена.",
            reply_markup=get_main_menu(ADMIN_ID)
        )
    else:
        await query.edit_message_text(
            "❌ Ошибка при одобрении заявки!",
            reply_markup=get_main_menu(ADMIN_ID)
        )

async def handle_reject_application(update: Update, context: ContextTypes.DEFAULT_TYPE, app_id):
    """Отклоняет заявку"""
    query = update.callback_query
    await query.answer()
    
    # Просим причину
    context.user_data['rejecting_app'] = app_id
    await query.edit_message_text(
        "📝 Введите причину отклонения заявки:"
    )
    
    return MESSAGE_REASON

async def reject_application_with_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклоняет заявку с причиной"""
    reason = update.message.text.strip()
    app_id = context.user_data.get('rejecting_app')
    
    if not app_id:
        await update.message.reply_text("❌ Ошибка!")
        return ConversationHandler.END
    
    if reject_application(app_id, reason):
        app = get_application(app_id)
        
        # Уведомляем пользователя
        try:
            await context.bot.send_message(
                app['user_id'],
                f"❌ **ВАША ЗАЯВКА #{app_id} ОТКЛОНЕНА**\n\n"
                f"📋 **Причина:** {reason}\n\n"
                f"Вы можете подать заявку снова."
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления: {e}")
        
        await update.message.reply_text(
            f"❌ Заявка #{app_id} отклонена!",
            reply_markup=get_main_menu(ADMIN_ID)
        )
    else:
        await update.message.reply_text(
            "❌ Ошибка при отклонении заявки!",
            reply_markup=get_main_menu(ADMIN_ID)
        )
    
    if 'rejecting_app' in context.user_data:
        del context.user_data['rejecting_app']
    
    return ConversationHandler.END

async def admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сообщения для админа"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ Нет доступа!")
        return
    
    pending_msgs = [m for m in messages_to_admin.values() if m['status'] == 'pending']
    
    if not pending_msgs:
        await query.edit_message_text(
            "📭 **Нет сообщений на рассмотрении**",
            reply_markup=get_main_menu(ADMIN_ID)
        )
        return
    
    text = f"✉️ **СООБЩЕНИЯ ОТ ПОЛЬЗОВАТЕЛЕЙ** ({len(pending_msgs)})\n\n"
    
    msg_types_text = {
        "premium": "💰 Премия",
        "job_change": "💼 Смена работы",
        "other": "📝 Сообщение"
    }
    
    for i, msg in enumerate(pending_msgs[:5], 1):
        text += f"{i}. **#{msg['id']}** - {msg['user']['nickname']}\n"
        text += f"   📋 {msg_types_text.get(msg['type'], 'Неизвестно')}\n\n"
    
    if len(pending_msgs) > 5:
        text += f"... и еще {len(pending_msgs) - 5} сообщений\n\n"
    
    keyboard = []
    for msg in pending_msgs[:3]:
        keyboard.append([
            InlineKeyboardButton(f"#{msg['id']} {msg['user']['nickname'][:15]}", callback_data=f"view_msg_{msg['id']}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def view_message_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, msg_id):
    """Просмотр сообщения админом"""
    query = update.callback_query
    await query.answer()
    
    msg = get_message(msg_id)
    if not msg:
        await query.edit_message_text("❌ Сообщение не найдено!")
        return
    
    msg_types_text = {
        "premium": "💰 Запрос премии",
        "job_change": "💼 Запрос смены работы",
        "other": "📝 Сообщение"
    }
    
    text = (
        f"✉️ **СООБЩЕНИЕ #{msg_id}**\n\n"
        f"📋 **Тип:** {msg_types_text.get(msg['type'], 'Неизвестно')}\n"
        f"👤 **От:** {msg['user']['nickname']} (@{msg['user'].get('username', 'нет')})\n"
        f"🆔 **ID:** {msg['user_id']}\n"
        f"📅 **Дата:** {msg['date']}\n\n"
        f"📝 **Сообщение:**\n{msg['text']}\n\n"
        f"📊 **Статус:** {msg['status']}"
    )
    
    if msg['status'] == 'pending':
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"msg_approve_{msg_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"msg_reject_{msg_id}")
            ],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_messages")]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_messages")]
        ])
    
    await query.edit_message_text(text, reply_markup=keyboard)

async def handle_message_approve(update: Update, context: ContextTypes.DEFAULT_TYPE, msg_id):
    """Одобряет сообщение"""
    query = update.callback_query
    await query.answer()
    
    msg = get_message(msg_id)
    if not msg:
        await query.edit_message_text("❌ Сообщение не найдено!")
        return
    
    update_message_status(msg_id, 'approved')
    
    # В зависимости от типа сообщения
    if msg['type'] == 'premium':
        # Можно добавить автоматическую выдачу премии
        text = f"✅ Сообщение #{msg_id} одобрено!\n\nТеперь вы можете выдать премию пользователю."
    else:
        text = f"✅ Сообщение #{msg_id} одобрено!"
    
    await query.edit_message_text(
        text,
        reply_markup=get_main_menu(ADMIN_ID)
    )
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            msg['user_id'],
            f"✅ **ВАШЕ СООБЩЕНИЕ #{msg_id} ОДОБРЕНО!**\n\n"
            f"Администратор рассмотрел ваше сообщение."
        )
    except Exception as e:
        logger.error(f"Ошибка уведомления: {e}")

async def handle_message_reject(update: Update, context: ContextTypes.DEFAULT_TYPE, msg_id):
    """Отклоняет сообщение"""
    query = update.callback_query
    await query.answer()
    
    # Просим причину
    context.user_data['rejecting_msg'] = msg_id
    await query.edit_message_text(
        "📝 Введите причину отклонения сообщения:"
    )

async def reject_message_with_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклоняет сообщение с причиной"""
    reason = update.message.text.strip()
    msg_id = context.user_data.get('rejecting_msg')
    
    if not msg_id:
        await update.message.reply_text("❌ Ошибка!")
        return ConversationHandler.END
    
    msg = get_message(msg_id)
    if not msg:
        await update.message.reply_text("❌ Сообщение не найдено!")
        return ConversationHandler.END
    
    update_message_status(msg_id, 'rejected')
    
    await update.message.reply_text(
        f"❌ Сообщение #{msg_id} отклонено!",
        reply_markup=get_main_menu(ADMIN_ID)
    )
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            msg['user_id'],
            f"❌ **ВАШЕ СООБЩЕНИЕ #{msg_id} ОТКЛОНЕНО**\n\n"
            f"📋 **Причина:** {reason}"
        )
    except Exception as e:
        logger.error(f"Ошибка уведомления: {e}")
    
    if 'rejecting_msg' in context.user_data:
        del context.user_data['rejecting_msg']
    
    return ConversationHandler.END

async def admin_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список пользователей для админа"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ Нет доступа!")
        return
    
    all_users = get_all_users()
    
    if not all_users:
        await query.edit_message_text(
            "📭 **Нет зарегистрированных пользователей**",
            reply_markup=get_main_menu(ADMIN_ID)
        )
        return
    
    text = f"👥 **ЗАРЕГИСТРИРОВАННЫЕ ПОЛЬЗОВАТЕЛИ** ({len(all_users)})\n\n"
    
    for i, user in enumerate(all_users[:10], 1):
        text += f"{i}. **{user['nickname']}**\n"
        text += f"   📱 @{user.get('username', 'нет')}\n"
        text += f"   💰 {user['coins']}🪙 | 👑 Ур. {user['level']}\n"
        text += f"   💼 {user['job']}\n\n"
    
    if len(all_users) > 10:
        text += f"... и еще {len(all_users) - 10} пользователей\n\n"
    
    text += "Выберите пользователя для управления:"
    
    keyboard = []
    for user in all_users[:5]:
        keyboard.append([
            InlineKeyboardButton(f"👤 {user['nickname'][:15]}", callback_data=f"manage_user_{user['user_id']}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def manage_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Управление пользователем"""
    query = update.callback_query
    await query.answer()
    
    user = get_user(user_id)
    if not user:
        await query.edit_message_text("❌ Пользователь не найден!")
        return
    
    text = (
        f"👤 **УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЕМ**\n\n"
        f"🎮 **Никнейм:** {user['nickname']}\n"
        f"📱 **Юзернейм:** @{user.get('username', 'нет')}\n"
        f"🆔 **ID:** {user_id}\n"
        f"💰 **Акойны:** {user['coins']} 🪙\n"
        f"👑 **Уровень:** {user['level']}\n"
        f"📈 **Опыт:** {user['exp']}/{user['level'] * 100}\n"
        f"💼 **Основная работа:** {user['job']}\n"
        f"💌 **Сообщений отправлено:** {user.get('messages_sent', 0)}\n"
        f"📅 **Регистрация:** {user.get('registration_date', '2026-01-02')}"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Выдать акойны", callback_data=f"give_coins_{user_id}"),
            InlineKeyboardButton("📈 Выдать опыт", callback_data=f"give_exp_{user_id}")
        ],
        [
            InlineKeyboardButton("⬆️ Повысить уровень", callback_data=f"level_up_{user_id}"),
            InlineKeyboardButton("⛔ Забанить", callback_data=f"ban_user_{user_id}")
        ],
        [InlineKeyboardButton("🔙 Назад к списку", callback_data="users_list")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_give_coins(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Начинает выдачу акойнов"""
    query = update.callback_query
    await query.answer()
    
    user = get_user(user_id)
    if not user:
        await query.edit_message_text("❌ Пользователь не найден!")
        return
    
    context.user_data['giving_coins_to'] = user_id
    await query.edit_message_text(
        f"💰 **ВЫДАЧА АКОЙНОВ**\n\n"
        f"👤 **Пользователь:** {user['nickname']}\n"
        f"💳 **Текущий баланс:** {user['coins']}🪙\n\n"
        f"Введите количество акойнов для выдачи:"
    )
    
    return GIVING_COINS

async def process_give_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выдачу акойнов"""
    try:
        amount = int(update.message.text.strip())
        user_id = context.user_data.get('giving_coins_to')
        
        if amount <= 0:
            await update.message.reply_text(
                "❌ Количество должно быть больше 0!\n"
                "Введите количество акойнов:"
            )
            return GIVING_COINS
        
        user = get_user(user_id)
        if not user:
            await update.message.reply_text(
                "❌ Пользователь не найден!",
                reply_markup=get_main_menu(ADMIN_ID)
            )
            return ConversationHandler.END
        
        new_balance = add_coins(user_id, amount)
        
        await update.message.reply_text(
            f"✅ **АКОЙНЫ ВЫДАНЫ!**\n\n"
            f"👤 **Пользователь:** {user['nickname']}\n"
            f"💰 **Выдано:** {amount} 🪙\n"
            f"💳 **Новый баланс:** {new_balance} 🪙",
            reply_markup=get_main_menu(ADMIN_ID)
        )
        
        # Уведомляем пользователя
        try:
            await context.bot.send_message(
                user_id,
                f"🎁 **ВЫ ПОЛУЧИЛИ {amount} АКОЙНОВ ОТ АДМИНИСТРАТОРА!**\n\n"
                f"💳 Ваш баланс: {new_balance} 🪙"
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления: {e}")
        
        # Очищаем данные
        if 'giving_coins_to' in context.user_data:
            del context.user_data['giving_coins_to']
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат! Введите число:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="users_list")]
            ])
        )
        return GIVING_COINS
    
    return ConversationHandler.END

async def start_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Начинает бан пользователя"""
    query = update.callback_query
    await query.answer()
    
    user = get_user(user_id)
    if not user:
        await query.edit_message_text("❌ Пользователь не найден!")
        return
    
    context.user_data['banning_user'] = user_id
    await query.edit_message_text(
        f"⛔ **БАН ПОЛЬЗОВАТЕЛЯ**\n\n"
        f"👤 **Пользователь:** {user['nickname']}\n"
        f"🆔 **ID:** {user_id}\n"
        f"💼 **Работа:** {user['job']}\n"
        f"💰 **Баланс:** {user['coins']}🪙\n\n"
        f"Введите причину бана:"
    )
    
    return BAN_REASON

async def process_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает бан пользователя"""
    reason = update.message.text.strip()
    user_id = context.user_data.get('banning_user')
    
    user = get_user(user_id)
    if not user:
        await update.message.reply_text(
            "❌ Пользователь не найден!",
            reply_markup=get_main_menu(ADMIN_ID)
        )
        return ConversationHandler.END
    
    ban_user(user_id, reason)
    
    await update.message.reply_text(
        f"⛔ **ПОЛЬЗОВАТЕЛЬ ЗАБАНЕН!**\n\n"
        f"👤 **Пользователь:** {user['nickname']}\n"
        f"📋 **Причина:** {reason}",
        reply_markup=get_main_menu(ADMIN_ID)
    )
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            user_id,
            f"⛔ **ВЫ БЫЛИ ЗАБАНЕНЫ В КЛАНЕ АД!**\n\n"
            f"📋 **Причина:** {reason}\n\n"
            f"Вы больше не можете использовать бота."
        )
    except Exception as e:
        logger.error(f"Ошибка уведомления: {e}")
    
    # Очищаем данные
    if 'banning_user' in context.user_data:
        del context.user_data['banning_user']
    
    return ConversationHandler.END

async def admin_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Задания для админа"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ Нет доступа!")
        return
    
    keyboard = [
        [InlineKeyboardButton("📝 Создать задание", callback_data="create_task_admin")],
        [InlineKeyboardButton("📋 Просмотреть задания", callback_data="view_tasks_admin")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    
    await query.edit_message_text(
        "📋 **УПРАВЛЕНИЕ ЗАДАНИЯМИ**\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def create_task_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание задания админом"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📝 **СОЗДАНИЕ ЗАДАНИЯ**\n\n"
        "Введите название задания:"
    )
    
    context.user_data['creating_task'] = True
    return CREATING_TASK_TITLE

async def create_task_title_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает название задания"""
    title = update.message.text.strip()
    context.user_data['task_title'] = title
    
    await update.message.reply_text(
        "📄 Введите описание задания:"
    )
    
    return CREATING_TASK_DESC

async def create_task_desc_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает описание задания"""
    description = update.message.text.strip()
    context.user_data['task_description'] = description
    
    await update.message.reply_text(
        "💰 Введите награду в акойнах:"
    )
    
    return CREATING_TASK_REWARD_COINS

async def create_task_reward_coins_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает награду в акойнах"""
    try:
        reward_coins = int(update.message.text.strip())
        context.user_data['reward_coins'] = reward_coins
        
        await update.message.reply_text(
            "📈 Введите награду в опыте:"
        )
        
        return CREATING_TASK_REWARD_EXP
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат! Введите число:"
        )
        return CREATING_TASK_REWARD_COINS

async def create_task_reward_exp_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает награду в опыте и создает задание"""
    try:
        reward_exp = int(update.message.text.strip())
        
        task_id = create_task(
            context.user_data['task_title'],
            context.user_data['task_description'],
            context.user_data['reward_coins'],
            reward_exp
        )
        
        await update.message.reply_text(
            f"✅ **ЗАДАНИЕ СОЗДАНО!**\n\n"
            f"📋 **Название:** {context.user_data['task_title']}\n"
            f"📝 **Описание:** {context.user_data['task_description']}\n"
            f"🎁 **Награда:** {context.user_data['reward_coins']}🪙 + {reward_exp} опыта\n"
            f"🆔 **ID задания:** #{task_id}",
            reply_markup=get_main_menu(ADMIN_ID)
        )
        
        # Очищаем данные
        context.user_data.clear()
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат! Введите число:"
        )
        return CREATING_TASK_REWARD_EXP
    
    return ConversationHandler.END

async def view_tasks_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр заданий админом"""
    query = update.callback_query
    await query.answer()
    
    active_tasks = get_active_tasks()
    
    if not active_tasks:
        await query.edit_message_text(
            "📭 **Нет активных заданий**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Создать задание", callback_data="create_task_admin")],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_tasks")]
            ])
        )
        return
    
    text = "📋 **АКТИВНЫЕ ЗАДАНИЯ**\n\n"
    
    for task in active_tasks:
        assigned = "✅ Назначено" if task['assigned_to'] else "⏳ Ожидает"
        text += f"🆔 **#{task['id']}** - {task['title']}\n"
        text += f"📝 {task['description'][:50]}...\n"
        text += f"🎁 {task['reward_coins']}🪙 + {task['reward_exp']} опыта\n"
        text += f"📊 Статус: {assigned}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("📝 Создать еще", callback_data="create_task_admin")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_tasks")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройки админа"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ Нет доступа!")
        return
    
    # Считаем статистику по работам
    jobs_stats = {}
    for user in get_all_users():
        for job in user.get('selected_jobs', []):
            jobs_stats[job] = jobs_stats.get(job, 0) + 1
    
    text = "⚙️ **НАСТРОЙКИ И СТАТИСТИКА**\n\n"
    text += "📊 **Занятость работ:**\n\n"
    
    for job_name, job_details in JOBS_DETAILS.items():
        current = jobs_stats.get(job_name, 0)
        max_count = job_details['max_users']
        percentage = (current / max_count) * 100 if max_count > 0 else 0
        
        progress_bar = "🟩" * int(percentage / 20) + "⬜" * (5 - int(percentage / 20))
        text += f"{job_name}: {progress_bar} {current}/{max_count}\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Обновить статистику", callback_data="admin_settings")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== ОБРАБОТЧИК CALLBACK ==========

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает все callback-запросы"""
    query = update.callback_query
    data = query.data
    
    await query.answer()
    
    # Основные кнопки
    if data == "back":
        await start(update, context)
    elif data == "profile":
        await show_profile(update, context)
    elif data == "my_jobs":
        await show_my_jobs(update, context)
    elif data == "tasks":
        await show_tasks(update, context)
    elif data == "top":
        await show_top(update, context)
    elif data == "send_message":
        await send_message_menu(update, context)
    elif data == "change_nick":
        await change_nickname(update, context)
        return CHANGING_NICKNAME
    elif data == "change_jobs":
        await change_jobs(update, context)
        return CHANGING_JOBS
    
    # Регистрация
    elif data.startswith("cat_"):
        category = data.replace("cat_", "")
        await show_category_jobs(update, context, category)
    elif data.startswith("job_toggle_"):
        job_name = data.replace("job_toggle_", "")
        await toggle_job_selection(update, context, job_name)
    elif data == "show_selected":
        await show_selected_jobs(update, context)
    elif data == "finish_selection":
        await show_selected_jobs(update, context)
    elif data == "back_to_categories":
        categories = get_categories()
        keyboard = []
        for category in categories:
            keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
        await query.edit_message_text(
            "💼 **ВЫБОР РАБОТ**\n\nВыберите категорию:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SELECTING_JOBS
    elif data == "confirm_selection":
        await confirm_selection(update, context)
        return CONFIRM_REGISTRATION
    elif data == "submit_registration":
        await submit_registration(update, context)
        return ConversationHandler.END
    
    # Сообщения админу
    elif data == "msg_premium":
        await start_message(update, context, "premium")
        return SENDING_MESSAGE
    elif data == "msg_job_change":
        await start_message(update, context, "job_change")
        return SENDING_MESSAGE
    elif data == "msg_other":
        await start_message(update, context, "other")
        return SENDING_MESSAGE
    
    # Админ панель
    elif data == "stats":
        await admin_stats(update, context)
    elif data == "applications":
        await admin_applications(update, context)
    elif data == "admin_tasks":
        await admin_tasks(update, context)
    elif data == "users_list":
        await admin_users_list(update, context)
    elif data == "admin_messages":
        await admin_messages(update, context)
    elif data == "admin_settings":
        await admin_settings(update, context)
    
    # Админ - заявки
    elif data.startswith("view_app_"):
        app_id = int(data.replace("view_app_", ""))
        await view_application_admin(update, context, app_id)
    elif data.startswith("do_approve_"):
        app_id = int(data.replace("do_approve_", ""))
        await handle_approve_application(update, context, app_id)
    elif data.startswith("do_reject_"):
        app_id = int(data.replace("do_reject_", ""))
        await handle_reject_application(update, context, app_id)
        return MESSAGE_REASON
    elif data.startswith("approve_"):
        app_id = int(data.replace("approve_", ""))
        await handle_approve_application(update, context, app_id)
    elif data.startswith("reject_"):
        app_id = int(data.replace("reject_", ""))
        await handle_reject_application(update, context, app_id)
        return MESSAGE_REASON
    
    # Админ - сообщения
    elif data.startswith("view_msg_"):
        msg_id = int(data.replace("view_msg_", ""))
        await view_message_admin(update, context, msg_id)
    elif data.startswith("msg_approve_"):
        msg_id = int(data.replace("msg_approve_", ""))
        await handle_message_approve(update, context, msg_id)
    elif data.startswith("msg_reject_"):
        msg_id = int(data.replace("msg_reject_", ""))
        await handle_message_reject(update, context, msg_id)
        return MESSAGE_REASON
    
    # Админ - пользователи
    elif data.startswith("manage_user_"):
        user_id = int(data.replace("manage_user_", ""))
        await manage_user(update, context, user_id)
    elif data.startswith("give_coins_"):
        user_id = int(data.replace("give_coins_", ""))
        await start_give_coins(update, context, user_id)
        return GIVING_COINS
    elif data.startswith("ban_user_"):
        user_id = int(data.replace("ban_user_", ""))
        await start_ban_user(update, context, user_id)
        return BAN_REASON
    
    # Админ - задания
    elif data == "create_task_admin":
        await create_task_admin(update, context)
        return CREATING_TASK_TITLE
    elif data == "view_tasks_admin":
        await view_tasks_admin(update, context)
    
    # Сохранение новых работ
    elif data == "save_new_jobs":
        await save_new_jobs(update, context)
        return ConversationHandler.END

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Хендлер для регистрации
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
                CallbackQueryHandler(handle_callback, pattern='^cat_|^job_toggle_|^show_selected|^finish_selection|^back_to_categories|^confirm_selection|^submit_registration')
            ],
            CONFIRM_REGISTRATION: [
                CallbackQueryHandler(handle_callback, pattern='^submit_registration|^back_to_categories')
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    # Хендлер для смены ника
    nick_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(change_nickname, pattern='^change_nick$')],
        states={
            CHANGING_NICKNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_new_nickname)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    # Хендлер для смены работ
    jobs_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(change_jobs, pattern='^change_jobs$')],
        states={
            CHANGING_JOBS: [
                CallbackQueryHandler(handle_callback, pattern='^cat_|^job_toggle_|^show_selected|^finish_selection|^back_to_categories|^save_new_jobs')
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    # Хендлер для отправки сообщений админу
    msg_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern='^msg_premium$|^msg_job_change$|^msg_other$')],
        states={
            SENDING_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_message)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    # Хендлер для отклонения заявок с причиной
    reject_app_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern='^do_reject_|^reject_')],
        states={
            MESSAGE_REASON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, reject_application_with_reason)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    # Хендлер для отклонения сообщений с причиной
    reject_msg_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern='^msg_reject_')],
        states={
            MESSAGE_REASON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, reject_message_with_reason)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    # Хендлер для выдачи акойнов
    coins_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern='^give_coins_')],
        states={
            GIVING_COINS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_give_coins)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    # Хендлер для бана пользователей
    ban_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern='^ban_user_')],
        states={
            BAN_REASON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_ban_user)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    # Хендлер для создания заданий
    task_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern='^create_task_admin$')],
        states={
            CREATING_TASK_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_task_title_admin)
            ],
            CREATING_TASK_DESC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_task_desc_admin)
            ],
            CREATING_TASK_REWARD_COINS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_task_reward_coins_admin)
            ],
            CREATING_TASK_REWARD_EXP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_task_reward_exp_admin)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    # Основные хендлеры
    application.add_handler(CommandHandler("start", start))
    application.add_handler(reg_conv_handler)
    application.add_handler(nick_conv_handler)
    application.add_handler(jobs_conv_handler)
    application.add_handler(msg_conv_handler)
    application.add_handler(reject_app_conv_handler)
    application.add_handler(reject_msg_conv_handler)
    application.add_handler(coins_conv_handler)
    application.add_handler(ban_conv_handler)
    application.add_handler(task_conv_handler)
    
    # Хендлер для всех остальных callback-запросов
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Запуск
    logger.info("Бот запускается...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()