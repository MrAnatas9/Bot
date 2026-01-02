# База данных в памяти
users = {}
applications = {}
tasks = {}
messages_to_admin = {}
user_tasks = {}
banned_users = set()
application_counter = 0
message_counter = 0
task_counter = 0

# Описания работ
JOBS_DETAILS = {
    "👑 Судья": {
        "category": "🏛️ Управление & Закон",
        "description": "Вершит правосудие, разрешает внутренние споры",
        "min_level": 10,
        "max_users": 2
    },
    "⚖️ Адвокат": {
        "category": "🏛️ Управление & Закон", 
        "description": "Защищает интересы членов клана в спорах",
        "min_level": 5,
        "max_users": 4
    },
    "🔍 Следователь": {
        "category": "🏛️ Управление & Закон",
        "description": "Расследует внутренние инциденты",
        "min_level": 7,
        "max_users": 2
    },
    "🕊️ Дипломат": {
        "category": "🏛️ Управление & Закон",
        "description": "Представляет клан вовне, ведёт переговоры",
        "min_level": 5,
        "max_users": 2
    },
    "📜 Архивариус": {
        "category": "🏛️ Управление & Закон",
        "description": "Систематизирует и ведет архив правил",
        "min_level": 3,
        "max_users": 2
    },
    "🛡️ Офицер Безопасности": {
        "category": "🏛️ Управление & Закон",
        "description": "Проверяет участников на благонадёжность",
        "min_level": 8,
        "max_users": 2
    },
    "🎥 Ютубер": {
        "category": "📢 Медиа & Творчество",
        "description": "Создает видеоконтент для привлечения людей",
        "min_level": 1,
        "max_users": 2
    },
    "📰 Журналист": {
        "category": "📢 Медиа & Творчество",
        "description": "Освещает внутренние и внешние события клана",
        "min_level": 1,
        "max_users": 3
    },
    "✍️ Писатель": {
        "category": "📢 Медиа & Творчество",
        "description": "Пишет истории и легенды клана",
        "min_level": 1,
        "max_users": 5
    },
    "🎨 Художник": {
        "category": "📢 Медиа & Творчество",
        "description": "Рисует арты для клана",
        "min_level": 1,
        "max_users": 4
    },
    "📢 Рекламист": {
        "category": "📢 Медиа & Творчество",
        "description": "Создаёт и распространяет рекламу клана",
        "min_level": 1,
        "max_users": 3
    },
    "🎙️ Ведущий": {
        "category": "📢 Медиа & Творчество",
        "description": "Организует внутриклановые мероприятия",
        "min_level": 2,
        "max_users": 3
    },
    "📱 SMM-менеджер": {
        "category": "📢 Медиа & Творчество",
        "description": "Отвечает за комментирование под видео",
        "min_level": 1,
        "max_users": 2
    },
    "💻 Программист": {
        "category": "⚙️ Профессии & Разработка",
        "description": "Разрабатывает плагины и боты для нужд клана",
        "min_level": 3,
        "max_users": 3
    },
    "🔨 Мастер": {
        "category": "⚙️ Профессии & Разработка",
        "description": "Ключевой организатор строительства",
        "min_level": 6,
        "max_users": 3
    },
    "🎬 Монтажёр": {
        "category": "⚙️ Профессии & Разработка",
        "description": "Помогает ютуберам создавая качественный контент",
        "min_level": 2,
        "max_users": 2
    },
    "🏗️ Строитель": {
        "category": "⚙️ Профессии & Разработка",
        "description": "Отвечает за возведение структур клана",
        "min_level": 1,
        "max_users": 5
    },
    "📊 Оператор": {
        "category": "⚙️ Профессии & Разработка",
        "description": "Записывает важные моменты клана",
        "min_level": 1,
        "max_users": 2
    },
    "🎮 Тестировщик": {
        "category": "⚙️ Профессии & Разработка",
        "description": "Проверяет новые плагины и механизмы",
        "min_level": 1,
        "max_users": 2
    },
    "📐 Архитектор": {
        "category": "⚙️ Профессии & Разработка",
        "description": "Создаёт детальные планы зданий",
        "min_level": 4,
        "max_users": 3
    },
    "👁️ Куратор": {
        "category": "📚 Поддержка & Наставничество",
        "description": "Ищет новых людей и помогает новичкам",
        "min_level": 2,
        "max_users": 5
    },
    "📖 Историк": {
        "category": "📚 Поддержка & Наставничество",
        "description": "Ведёт хронику клана",
        "min_level": 3,
        "max_users": 2
    },
    "🧭 Гид": {
        "category": "📚 Поддержка & Наставничество",
        "description": "Проводит экскурсии по владениям клана",
        "min_level": 1,
        "max_users": 2
    },
    "🤝 Психолог": {
        "category": "📚 Поддержка & Наставничество",
        "description": "Помогает разрешать личные конфликты",
        "min_level": 4,
        "max_users": 2
    },
    "🏹 Разведчик": {
        "category": "🎭 Оборона & Разведка",
        "description": "Собирает информацию о других кланах",
        "min_level": 6,
        "max_users": 2
    }
}

# Инициализируем админа
users[6495178643] = {
    'user_id': 6495178643,
    'username': 'admin',
    'nickname': '👑 Глава Клана',
    'job': '👑 Глава Клана',
    'selected_jobs': ['👑 Глава Клана'],
    'coins': 999999,
    'level': 10,
    'exp': 0,
    'messages_sent': 0,
    'is_admin': True,
    'registration_date': '2026-01-02'
}

def save_user(user_id, username, nickname, selected_jobs):
    """Сохраняет пользователя"""
    if user_id not in users:
        users[user_id] = {
            'user_id': user_id,
            'username': username,
            'nickname': nickname,
            'job': selected_jobs[0] if selected_jobs else 'Безработный',
            'selected_jobs': selected_jobs,
            'coins': 100,  # Начальные деньги
            'level': 1,
            'exp': 0,
            'messages_sent': 0,
            'is_admin': False,
            'registration_date': '2026-01-02'
        }
        return True
    return False

def get_user(user_id):
    """Получает пользователя"""
    if user_id in banned_users:
        return None
    return users.get(user_id)

def get_all_users():
    """Получает всех пользователей"""
    return [u for u in users.values() if not u.get('is_admin', False)]

def save_application(user_id, username, nickname, source, selected_jobs):
    """Сохраняет заявку"""
    global application_counter
    application_counter += 1
    app_id = application_counter
    
    applications[app_id] = {
        'id': app_id,
        'user_id': user_id,
        'username': username,
        'nickname': nickname,
        'source': source,
        'selected_jobs': selected_jobs,
        'status': 'pending',
        'date': '2026-01-02'
    }
    return app_id

def get_application(app_id):
    """Получает заявку"""
    return applications.get(app_id)

def approve_application(app_id):
    """Одобряет заявку"""
    if app_id in applications:
        app = applications[app_id]
        app['status'] = 'approved'
        save_user(app['user_id'], app['username'], app['nickname'], app['selected_jobs'])
        return True
    return False

def reject_application(app_id, reason=""):
    """Отклоняет заявку"""
    if app_id in applications:
        applications[app_id]['status'] = 'rejected'
        applications[app_id]['reason'] = reason
        return True
    return False

def update_user_nickname(user_id, new_nickname):
    """Обновляет никнейм пользователя"""
    if user_id in users:
        users[user_id]['nickname'] = new_nickname
        return True
    return False

def update_user_jobs(user_id, selected_jobs):
    """Обновляет работы пользователя"""
    if user_id in users:
        users[user_id]['selected_jobs'] = selected_jobs
        users[user_id]['job'] = selected_jobs[0] if selected_jobs else 'Безработный'
        return True
    return False

def ban_user(user_id, reason=""):
    """Банит пользователя"""
    banned_users.add(user_id)
    if user_id in users:
        del users[user_id]
    return True

def unban_user(user_id):
    """Разбанивает пользователя"""
    if user_id in banned_users:
        banned_users.remove(user_id)
        return True
    return False

def add_coins(user_id, amount):
    """Добавляет акойны"""
    if user_id in users:
        users[user_id]['coins'] += amount
        return users[user_id]['coins']
    return None

def add_exp(user_id, amount):
    """Добавляет опыт"""
    if user_id in users:
        users[user_id]['exp'] += amount
        # Проверка повышения уровня
        exp_needed = users[user_id]['level'] * 100
        if users[user_id]['exp'] >= exp_needed:
            users[user_id]['level'] += 1
            users[user_id]['exp'] = 0
            return True, users[user_id]['level']  # Уровень повышен
        return False, users[user_id]['level']  # Уровень не изменился
    return None, None

def create_task(title, description, reward_coins, reward_exp):
    """Создает задание"""
    global task_counter
    task_counter += 1
    task_id = task_counter
    
    tasks[task_id] = {
        'id': task_id,
        'title': title,
        'description': description,
        'reward_coins': reward_coins,
        'reward_exp': reward_exp,
        'status': 'active',
        'assigned_to': None
    }
    return task_id

def get_active_tasks():
    """Получает активные задания"""
    return [t for t in tasks.values() if t['status'] == 'active']

def assign_task(task_id, user_id):
    """Назначает задание пользователю"""
    if task_id in tasks and tasks[task_id]['status'] == 'active':
        tasks[task_id]['status'] = 'in_progress'
        tasks[task_id]['assigned_to'] = user_id
        return True
    return False

def complete_task(task_id):
    """Завершает задание"""
    if task_id in tasks and tasks[task_id]['status'] == 'in_progress':
        tasks[task_id]['status'] = 'completed'
        user_id = tasks[task_id]['assigned_to']
        
        # Выдаем награду
        task = tasks[task_id]
        if user_id in users:
            users[user_id]['coins'] += task['reward_coins']
            add_exp(user_id, task['reward_exp'])
        
        return True
    return False

def save_message_to_admin(user_id, message_type, text):
    """Сохраняет сообщение для админа"""
    global message_counter
    message_counter += 1
    msg_id = message_counter
    
    messages_to_admin[msg_id] = {
        'id': msg_id,
        'user_id': user_id,
        'user': get_user(user_id),
        'type': message_type,  # 'premium', 'job_change', 'other'
        'text': text,
        'status': 'pending',
        'date': '2026-01-02'
    }
    
    # Увеличиваем счетчик сообщений пользователя
    if user_id in users:
        users[user_id]['messages_sent'] += 1
    
    return msg_id

def get_messages_to_admin():
    """Получает все сообщения для админа"""
    return list(messages_to_admin.values())

def get_message(msg_id):
    """Получает сообщение по ID"""
    return messages_to_admin.get(msg_id)

def update_message_status(msg_id, status):
    """Обновляет статус сообщения"""
    if msg_id in messages_to_admin:
        messages_to_admin[msg_id]['status'] = status
        return True
    return False

def get_jobs_by_category(category=None):
    """Получает работы по категории"""
    if category:
        return {k: v for k, v in JOBS_DETAILS.items() if v['category'] == category}
    return JOBS_DETAILS

def get_categories():
    """Получает все категории"""
    categories = set()
    for job_details in JOBS_DETAILS.values():
        categories.add(job_details['category'])
    return list(categories)

def get_users_count_by_job(job_name):
    """Считает количество пользователей с определенной работой"""
    count = 0
    for user in users.values():
        if job_name in user.get('selected_jobs', []):
            count += 1
    return count

def is_job_available(job_name):
    """Проверяет доступность работы (не превышен ли лимит)"""
    if job_name not in JOBS_DETAILS:
        return False
    
    max_users = JOBS_DETAILS[job_name]['max_users']
    current_users = get_users_count_by_job(job_name)
    
    return current_users < max_users
