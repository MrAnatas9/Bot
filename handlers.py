import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database import *
from config import *

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(
    ASKING_NICKNAME, ASKING_SOURCE, SELECTING_JOBS, 
    CONFIRM_REGISTRATION, CHANGING_NICKNAME, SENDING_MESSAGE,
    CREATING_TASK_TITLE, CREATING_TASK_DESC, CREATING_TASK_REWARD_COINS, 
    CREATING_TASK_REWARD_EXP, BAN_REASON, MESSAGE_REASON,
    GIVING_COINS, CHANGING_JOBS, TASK_PROOF, TRANSFER_AMOUNT
) = range(16)

# ========== ОБЩИЕ ФУНКЦИИ ==========
def get_main_menu(user_id: int) -> InlineKeyboardMarkup:
    """Создает главное меню в зависимости от пользователя"""
    user = get_user(user_id)
    
    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("📝 Заявки", callback_data="applications")],
            [InlineKeyboardButton("📋 Задания", callback_data="admin_tasks")],
            [InlineKeyboardButton("👥 Пользователи", callback_data="users_list")],
            [InlineKeyboardButton("💌 Сообщения", callback_data="admin_messages")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings")]
        ]
    elif user:
        keyboard = [
            [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
            [InlineKeyboardButton("📋 Задания", callback_data="tasks")],
            [InlineKeyboardButton("💼 Мои работы", callback_data="my_jobs")],
            [InlineKeyboardButton("🏆 Топ", callback_data="top")],
            [InlineKeyboardButton("💰 Перевод", callback_data="transfer")],
            [InlineKeyboardButton("✉️ Админу", callback_data="send_message")],
            [
                InlineKeyboardButton("🔄 Ник", callback_data="change_nick"),
                InlineKeyboardButton("🔄 Работы", callback_data="change_jobs")
            ],
            [InlineKeyboardButton("📞 Поддержка", url="https://t.me/MrAnatas")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🚀 Регистрация", callback_data="register")],
            [InlineKeyboardButton("📞 Поддержка", url="https://t.me/MrAnatas")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

# ========== НАЧАЛЬНЫЕ КОМАНДЫ ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            f"👋 Привет, {user.first_name}!\n"
            f"👹 Добро пожаловать в бот клана АД!\n\n"
            f"Выберите действие:",
            reply_markup=get_main_menu(user.id)
        )

# ========== РЕГИСТРАЦИЯ ==========
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс регистрации"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    if get_user(user.id):
        await query.edit_message_text(
            "✅ Вы уже зарегистрированы!",
            reply_markup=get_main_menu(user.id)
        )
        return ConversationHandler.END
    
    await query.edit_message_text(
        "📝 **РЕГИСТРАЦИЯ В КЛАНЕ**\n\n"
        "Введите ваш игровой никнейм (минимум 3 символа):"
    )
    
    context.user_data['selected_jobs'] = []
    return ASKING_NICKNAME

async def ask_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принимает никнейм"""
    nickname = update.message.text.strip()
    
    if len(nickname) < 3:
        await update.message.reply_text("❌ Никнейм должен быть не менее 3 символов.\nПопробуйте снова:")
        return ASKING_NICKNAME
    
    context.user_data['nickname'] = nickname
    await update.message.reply_text(
        "📌 **Откуда вы узнали о клане?**\n"
        "(друг, поиск, реклама и т.д.)"
    )
    
    return ASKING_SOURCE

async def ask_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принимает источник"""
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
        f"💡 Все работы доступны с **1 уровня**!\n"
        f"📊 Можно выбрать до **{MAX_JOBS_PER_USER}** работ\n\n"
        "Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return SELECTING_JOBS

async def show_category_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Показывает работы в выбранной категории"""
    query = update.callback_query
    await query.answer()
    
    jobs = get_jobs_by_category(category)
    
    text = f"💼 **{category}**\n\n"
    text += "Выберите работу (можно до 3):\n\n"
    
    keyboard = []
    selected_count = len(context.user_data.get('selected_jobs', []))
    
    for job_name, job_details in jobs.items():
        available = is_job_available(job_name)
        current_count = get_users_count_by_job(job_name)
        max_count = job_details['max_users']
        
        status = "✅" if available else "❌"
        availability = f"({current_count}/{max_count})"
        
        if job_name in context.user_data.get('selected_jobs', []):
            text += f"✓ {job_name} {availability}\n"
        else:
            text += f"{status} {job_name} {availability}\n"
        
        # Кнопки
        if job_name in context.user_data.get('selected_jobs', []):
            keyboard.append([InlineKeyboardButton(f"❌ Убрать {job_name}", callback_data=f"job_toggle_{job_name}")])
        elif available and selected_count < MAX_JOBS_PER_USER:
            keyboard.append([InlineKeyboardButton(f"✅ Выбрать {job_name}", callback_data=f"job_toggle_{job_name}")])
        else:
            if not available:
                keyboard.append([InlineKeyboardButton(f"❌ {job_name} (нет мест)", callback_data="no_action")])
            elif selected_count >= MAX_JOBS_PER_USER:
                keyboard.append([InlineKeyboardButton(f"❌ {job_name} (лимит {MAX_JOBS_PER_USER})", callback_data="no_action")])
    
    keyboard.append([InlineKeyboardButton("📋 Мои выбранные работы", callback_data="show_selected")])
    keyboard.append([InlineKeyboardButton("✅ Завершить выбор", callback_data="finish_selection")])
    keyboard.append([InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_categories")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def toggle_job_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, job_name: str):
    """Добавляет/убирает работу из выбранных"""
    query = update.callback_query
    await query.answer()
    
    selected_jobs = context.user_data.get('selected_jobs', [])
    
    if job_name in selected_jobs:
        selected_jobs.remove(job_name)
        await query.answer(f"❌ {job_name} удалена")
    else:
        if len(selected_jobs) >= MAX_JOBS_PER_USER:
            await query.answer(f"❌ Максимум {MAX_JOBS_PER_USER} работ!")
            return
        
        if not is_job_available(job_name):
            await query.answer("❌ Нет свободных мест!")
            return
        
        selected_jobs.append(job_name)
        await query.answer(f"✅ {job_name} добавлена")
    
    context.user_data['selected_jobs'] = selected_jobs
    
    # Обновляем отображение
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
        text += f"{i}. {job_name}\n"
    
    text += f"\nВсего: {len(selected_jobs)}/{MAX_JOBS_PER_USER}"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Изменить выбор", callback_data="back_to_categories")],
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_selection")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def confirm_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение регистрации"""
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
        return CONFIRM_REGISTRATION
    
    text = "📋 **ПОДТВЕРЖДЕНИЕ РЕГИСТРАЦИИ**\n\n"
    text += f"👤 **Никнейм:** {context.user_data['nickname']}\n"
    text += f"📌 **Источник:** {context.user_data['source']}\n\n"
    text += "💼 **Выбранные работы:**\n"
    
    for job_name in selected_jobs:
        text += f"• {job_name}\n"
    
    text += f"\nВсего выбрано работ: {len(selected_jobs)}/{MAX_JOBS_PER_USER}\n\n"
    text += "Всё верно?"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, отправить", callback_data="submit_registration"),
            InlineKeyboardButton("❌ Нет, изменить", callback_data="back_to_categories")
        ]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM_REGISTRATION

async def submit_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение регистрации"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    selected_jobs = context.user_data.get('selected_jobs', [])
    
    # Сохраняем пользователя
    success = save_user(user.id, user.username, context.user_data['nickname'], selected_jobs)
    
    if success:
        await query.edit_message_text(
            f"✅ **РЕГИСТРАЦИЯ УСПЕШНА!**\n\n"
            f"👤 **Ваш никнейм:** {context.user_data['nickname']}\n"
            f"💼 **Выбранные работы:** {len(selected_jobs)}\n"
            f"💰 **Стартовые акойны:** {START_COINS}\n"
            f"👑 **Уровень:** 1\n\n"
            f"🔗 **Ссылка на чат клана:** {CLAN_LINK}\n"
            f"📞 **Поддержка:** @MrAnatas\n\n"
            f"Слава Аду! 👹",
            reply_markup=get_main_menu(user.id)
        )
    else:
        await query.edit_message_text(
            "❌ Ошибка при регистрации! Попробуйте позже.",
            reply_markup=get_main_menu(user.id)
        )
    
    context.user_data.clear()
    return ConversationHandler.END

# ========== ГРУППОВЫЕ КОМАНДЫ ==========
async def handle_group_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команд в группе"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip().lower()
    user = update.effective_user
    reply_to = update.message.reply_to_message
    
    # Команда "забрать"
    if text.startswith("забрать"):
        if not reply_to:
            await update.message.reply_text("❌ Ответьте на сообщение пользователя!")
            return
        
        target_user = reply_to.from_user
        current_user_data = get_user(user.id)
        target_user_data = get_user(target_user.id)
        
        if not current_user_data:
            await update.message.reply_text("❌ Вы не зарегистрированы в боте! Используйте /start")
            return
        
        if not target_user_data:
            await update.message.reply_text("❌ Этот пользователь не зарегистрирован в боте!")
            return
        
        # Парсим сумму
        try:
            parts = text.split()
            amount = int(parts[1]) if len(parts) > 1 else 0
            
            if amount <= 0:
                await update.message.reply_text("❌ Укажите положительную сумму!")
                return
        except:
            await update.message.reply_text("❌ Используйте: забрать <сумма>")
            return
        
        # Выполняем перевод
        success, message = transfer_coins(target_user.id, user.id, amount, "Забрать в группе")
        
        if success:
            await update.message.reply_text(
                f"✅ {user.first_name} забрал {amount} акойнов у {target_user.first_name}\n"
                f"💰 Новый баланс:\n"
                f"👤 {user.first_name}: {get_user_balance(user.id)} акойнов\n"
                f"👤 {target_user.first_name}: {get_user_balance(target_user.id)} акойнов"
            )
        else:
            await update.message.reply_text(f"❌ {message}")
    
    # Команда "выдать"
    elif text.startswith("выдать"):
        if not reply_to:
            await update.message.reply_text("❌ Ответьте на сообщение пользователя!")
            return
        
        target_user = reply_to.from_user
        current_user_data = get_user(user.id)
        target_user_data = get_user(target_user.id)
        
        if not current_user_data:
            await update.message.reply_text("❌ Вы не зарегистрированы в боте! Используйте /start")
            return
        
        if not target_user_data:
            await update.message.reply_text("❌ Этот пользователь не зарегистрирован в боте!")
            return
        
        # Парсим сумму
        try:
            parts = text.split()
            amount = int(parts[1]) if len(parts) > 1 else 0
            
            if amount <= 0:
                await update.message.reply_text("❌ Укажите положительную сумму!")
                return
        except:
            await update.message.reply_text("❌ Используйте: выдать <сумма>")
            return
        
        # Выполняем перевод
        success, message = transfer_coins(user.id, target_user.id, amount, "Выдать в группе")
        
        if success:
            await update.message.reply_text(
                f"✅ {user.first_name} выдал {amount} акойнов {target_user.first_name}\n"
                f"💰 Новый баланс:\n"
                f"👤 {user.first_name}: {get_user_balance(user.id)} акойнов\n"
                f"👤 {target_user.first_name}: {get_user_balance(target_user.id)} акойнов"
            )
        else:
            await update.message.reply_text(f"❌ {message}")
    
    # Команда "уволить" (только админ)
    elif text.startswith("уволить") and user.id == ADMIN_ID:
        if not reply_to:
            await update.message.reply_text("❌ Ответьте на сообщение пользователя!")
            return
        
        target_user = reply_to.from_user
        target_user_data = get_user(target_user.id)
        
        if not target_user_data:
            await update.message.reply_text("❌ Этот пользователь не зарегистрирован!")
            return
        
        # Увольняем
        success, message = fire_user(target_user.id, "Уволен в группе")
        
        if success:
            await update.message.reply_text(
                f"⛔ Администратор уволил {target_user.first_name}!\n"
                f"💼 Все работы сняты."
            )
        else:
            await update.message.reply_text(f"❌ {message}")
    
    # Команда "баланс"
    elif text == "баланс":
        user_data = get_user(user.id)
        if not user_data:
            await update.message.reply_text("❌ Вы не зарегистрированы в боте!")
            return
        
        balance = user_data['coins']
        if balance >= 0:
            await update.message.reply_text(f"💰 Ваш баланс: {balance} акойнов")
        else:
            await update.message.reply_text(f"⚠️ Ваш баланс: {balance} акойнов (долг: {-balance})")

# ========== CALLBACK ОБРАБОТЧИК ==========
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка callback-запросов"""
    query = update.callback_query
    data = query.data
    
    await query.answer()
    
    # Основные команды
    if data == "back":
        await start_command(update, context)
        return ConversationHandler.END
    
    elif data == "profile":
        await show_profile(update, context)
    
    elif data == "register":
        await start_registration(update, context)
        return ASKING_NICKNAME
    
    elif data == "tasks":
        await show_tasks(update, context)
    
    elif data == "transfer":
        await start_transfer(update, context)
        return TRANSFER_AMOUNT
    
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
        keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in categories]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
        await query.edit_message_text(
            "💼 **ВЫБОР РАБОТ**\n\nВыберите категорию:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "confirm_selection":
        await confirm_selection(update, context)
        return CONFIRM_REGISTRATION
    
    elif data == "submit_registration":
        await submit_registration(update, context)
        return ConversationHandler.END
    
    # Задания
    elif data.startswith("take_task_"):
        task_id = int(data.replace("take_task_", ""))
        await take_task(update, context, task_id)
    
    elif data.startswith("submit_proof_"):
        task_id = int(data.replace("submit_proof_", ""))
        context.user_data['task_id'] = task_id
        await query.edit_message_text("📸 Отправьте скриншот выполнения задания:")
        return TASK_PROOF
    
    # Переводы
    elif data.startswith("transfer_"):
        target_id = int(data.replace("transfer_", ""))
        context.user_data['transfer_target'] = target_id
        await query.edit_message_text("💸 Введите сумму для перевода:")
        return TRANSFER_AMOUNT

# ========== ПРОФИЛЬ ==========
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает профиль пользователя"""
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
    
    debt_status = "✅" if user['coins'] >= 0 else "⚠️"
    debt_text = f"Долг: {-user['coins']}🪙" if user['coins'] < 0 else "Без долгов"
    
    text = (
        f"👤 **ПРОФИЛЬ**\n\n"
        f"🎮 **Никнейм:** {user['nickname']}\n"
        f"📱 **TG:** @{user.get('username', 'нет')}\n"
        f"👑 **Уровень:** {user['level']}\n"
        f"📈 **Опыт:** {user['exp']}/{user['level'] * EXP_PER_LEVEL}\n"
        f"💰 **Акойны:** {user['coins']}🪙 {debt_status}\n"
        f"📊 **{debt_text}**\n"
        f"💼 **Основная работа:** {user['job']}\n"
        f"💌 **Сообщений:** {user.get('messages_sent', 0)}\n"
        f"🆔 **ID:** {user['user_id']}"
    )
    
    await query.edit_message_text(text, reply_markup=get_main_menu(user_id))

# ========== ЗАДАНИЯ ==========
async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает доступные задания"""
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
    
    tasks = get_active_tasks()
    
    if not tasks:
        await query.edit_message_text(
            "📭 **Нет активных заданий**\n\n"
            "Задания создает администратор.",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    text = "📋 **ДОСТУПНЫЕ ЗАДАНИЯ**\n\n"
    keyboard = []
    
    for task in tasks[:5]:
        assigned = "✅ Взято" if task['assigned_to'] else "⏳ Свободно"
        text += f"📌 **{task['title']}**\n"
        text += f"📝 {task['description'][:50]}...\n"
        text += f"🎁 Награда: {task['reward_coins']}🪙 + {task['reward_exp']} опыта\n"
        text += f"⏰ Статус: {assigned}\n\n"
        
        if not task['assigned_to']:
            keyboard.append([
                InlineKeyboardButton(f"📋 Взять: {task['title'][:15]}", callback_data=f"take_task_{task['id']}")
            ])
    
    if keyboard:
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.edit_message_text(
            "📭 **Все задания взяты**\n\n"
            "Ожидайте новых заданий.",
            reply_markup=get_main_menu(user_id)
        )

async def take_task(update: Update, context: ContextTypes.DEFAULT_TYPE, task_id: int):
    """Берет задание"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    success, message = assign_task(task_id, user_id)
    
    if success:
        task = get_task(task_id)
        await query.edit_message_text(
            f"✅ **ЗАДАНИЕ ВЗЯТО!**\n\n"
            f"📋 **Задание:** {task['title']}\n"
            f"📝 **Описание:** {task['description']}\n"
            f"⏰ **Срок:** {TASK_DEADLINE_HOURS} часов\n"
            f"🎁 **Награда:** {task['reward_coins']}🪙 + {task['reward_exp']} опыта\n\n"
            f"⚠️ **Внимание:**\n"
            f"- При просрочке штраф {TASK_PENALTY_PERCENT*100}% от награды\n"
            f"- После выполнения отправьте proof через кнопку ниже",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📸 Отправить proof", callback_data=f"submit_proof_{task_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data="tasks")]
            ])
        )
    else:
        await query.edit_message_text(
            f"❌ {message}",
            reply_markup=get_main_menu(user_id)
        )

async def handle_task_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка proof задания"""
    user_id = update.effective_user.id
    task_id = context.user_data.get('task_id')
    
    if not task_id:
        await update.message.reply_text(
            "❌ Ошибка. Начните заново.",
            reply_markup=get_main_menu(user_id)
        )
        return ConversationHandler.END
    
    proof_text = update.message.text or "Proof отправлен"
    
    success, message = submit_task_proof(task_id, user_id, proof_text)
    
    if success:
        # Уведомление админу
        task = get_task(task_id)
        user = get_user(user_id)
        
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            await context.bot.send_message(
                ADMIN_ID,
                f"📸 **НОВЫЙ PROOF ЗАДАНИЯ**\n\n"
                f"👤 Пользователь: {user['nickname']}\n"
                f"📋 Задание: {task['title']}\n"
                f"📝 Proof: {proof_text[:100]}...\n"
                f"🆔 ID задания: {task_id}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_task_{task_id}"),
                        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_task_{task_id}")
                    ]
                ])
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления админа: {e}")
        
        await update.message.reply_text(
            "✅ **PROOF ОТПРАВЛЕН!**\n\n"
            "Администратор проверит выполнение задания.",
            reply_markup=get_main_menu(user_id)
        )
    else:
        await update.message.reply_text(
            f"❌ {message}",
            reply_markup=get_main_menu(user_id)
        )
    
    return ConversationHandler.END

# ========== ПЕРЕВОДЫ ==========
async def start_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс перевода"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "💸 **ПЕРЕВОД АКОЙНОВ**\n\n"
        "Введите в формате:\n"
        "<ID_получателя> <сумма>\n\n"
        "Пример: 123456789 50",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ])
    )
    
    return TRANSFER_AMOUNT

async def process_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает перевод"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    try:
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ Формат: <ID_получателя> <сумма>")
            return TRANSFER_AMOUNT
        
        target_id = int(parts[0])
        amount = int(parts[1])
        
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть положительной!")
            return TRANSFER_AMOUNT
        
        success, message = transfer_coins(user_id, target_id, amount, "Перевод через бота")
        
        await update.message.reply_text(
            f"{'✅' if success else '❌'} {message}",
            reply_markup=get_main_menu(user_id)
        )
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ Неверный формат чисел!")
        return TRANSFER_AMOUNT
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
        return TRANSFER_AMOUNT
