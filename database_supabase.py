import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

# Подключение к Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://oomxbawrjmqczezdpaqp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_secret_yF3kBESRC2YLxW4427qUjQ_gs1hG5LD")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Описания работ (скопировано из вашего database.py)
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

# Пустые словари для совместимости со старым кодом
users = {}
applications = {}
tasks = {}
messages_to_admin = {}
user_tasks = {}
banned_users = set()
application_counter = 0
message_counter = 0
task_counter = 0

# Инициализация админа
def initialize_admin():
    admin_id = 6495178643
    response = supabase.table('users').select('*').eq('user_id', admin_id).execute()
    
    if not response.data:
        admin_data = {
            'user_id': admin_id,
            'username': 'admin',
            'nickname': '👑 Глава Клана',
            'job': '👑 Глава Клана',
            'selected_jobs': ['👑 Глава Клана'],
            'coins': 999999,
            'level': 10,
            'exp': 0,
            'messages_sent': 0,
            'is_admin': True
        }
        supabase.table('users').insert(admin_data).execute()

# ========== ФУНКЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========

def save_user(user_id, username, nickname, selected_jobs):
    """Сохраняет пользователя"""
    user_data = {
        'user_id': user_id,
        'username': username,
        'nickname': nickname,
        'job': selected_jobs[0] if selected_jobs else 'Безработный',
        'selected_jobs': selected_jobs,
        'coins': 100,
        'level': 1,
        'exp': 0,
        'messages_sent': 0,
        'is_admin': False
    }
    response = supabase.table('users').upsert(user_data).execute()
    return bool(response.data)

def get_user(user_id):
    """Получает пользователя"""
    # Проверяем бан
    response = supabase.table('banned_users').select('*').eq('user_id', user_id).execute()
    if response.data:
        return None
    
    response = supabase.table('users').select('*').eq('user_id', user_id).execute()
    return response.data[0] if response.data else None

def get_all_users():
    """Получает всех пользователей"""
    response = supabase.table('users').select('*').eq('is_admin', False).execute()
    return response.data if response.data else []

# ========== ФУНКЦИИ ДЛЯ ЗАЯВОК ==========

def save_application(user_id, username, nickname, source, selected_jobs):
    """Сохраняет заявку"""
    app_data = {
        'user_id': user_id,
        'username': username,
        'nickname': nickname,
        'source': source,
        'selected_jobs': selected_jobs,
        'status': 'pending'
    }
    response = supabase.table('applications').insert(app_data).execute()
    return response.data[0]['id'] if response.data else 0

def get_application(app_id):
    """Получает заявку"""
    response = supabase.table('applications').select('*').eq('id', app_id).execute()
    return response.data[0] if response.data else None

def approve_application(app_id):
    """Одобряет заявку"""
    response = supabase.table('applications').select('*').eq('id', app_id).execute()
    if not response.data:
        return False
    
    app = response.data[0]
    
    # Обновляем статус заявки
    supabase.table('applications').update({'status': 'approved'}).eq('id', app_id).execute()
    
    # Сохраняем пользователя
    save_user(app['user_id'], app['username'], app['nickname'], app['selected_jobs'])
    
    return True

def reject_application(app_id, reason=""):
    """Отклоняет заявку"""
    response = supabase.table('applications').update({
        'status': 'rejected',
        'reason': reason
    }).eq('id', app_id).execute()
    return bool(response.data)

# ========== ОБНОВЛЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЯ ==========

def update_user_nickname(user_id, new_nickname):
    """Обновляет никнейм пользователя"""
    response = supabase.table('users').update({
        'nickname': new_nickname
    }).eq('user_id', user_id).execute()
    return bool(response.data)

def update_user_jobs(user_id, selected_jobs):
    """Обновляет работы пользователя"""
    response = supabase.table('users').update({
        'selected_jobs': selected_jobs,
        'job': selected_jobs[0] if selected_jobs else 'Безработный'
    }).eq('user_id', user_id).execute()
    return bool(response.data)

# ========== БАН И САНКЦИИ ==========

def ban_user(user_id, reason=""):
    """Банит пользователя"""
    # Добавляем в таблицу забаненных
    supabase.table('banned_users').insert({
        'user_id': user_id,
        'reason': reason
    }).execute()
    
    # Удаляем из пользователей
    supabase.table('users').delete().eq('user_id', user_id).execute()
    
    return True

def unban_user(user_id):
    """Разбанивает пользователя"""
    response = supabase.table('banned_users').delete().eq('user_id', user_id).execute()
    return bool(response.data)

# ========== АКОЙНЫ И ОПЫТ ==========

def add_coins(user_id, amount):
    """Добавляет акойны"""
    user = get_user(user_id)
    if not user:
        return None
    
    new_coins = user['coins'] + amount
    response = supabase.table('users').update({
        'coins': new_coins
    }).eq('user_id', user_id).execute()
    
    return new_coins if response.data else None

def add_exp(user_id, amount):
    """Добавляет опыт"""
    user = get_user(user_id)
    if not user:
        return None, None
    
    new_exp = user['exp'] + amount
    exp_needed = user['level'] * 100
    new_level = user['level']
    
    if new_exp >= exp_needed:
        new_level += 1
        new_exp = 0
    
    response = supabase.table('users').update({
        'exp': new_exp,
        'level': new_level
    }).eq('user_id', user_id).execute()
    
    return (new_exp >= exp_needed, new_level) if response.data else (None, None)

# ========== ЗАДАНИЯ ==========

def create_task(title, description, reward_coins, reward_exp):
    """Создает задание"""
    task_data = {
        'title': title,
        'description': description,
        'reward_coins': reward_coins,
        'reward_exp': reward_exp,
        'status': 'active',
        'assigned_to': None
    }
    response = supabase.table('tasks').insert(task_data).execute()
    return response.data[0]['id'] if response.data else 0

def get_active_tasks():
    """Получает активные задания"""
    response = supabase.table('tasks').select('*').eq('status', 'active').execute()
    return response.data if response.data else []

def assign_task(task_id, user_id):
    """Назначает задание пользователю"""
    response = supabase.table('tasks').update({
        'status': 'in_progress',
        'assigned_to': user_id
    }).eq('id', task_id).execute()
    return bool(response.data)

def complete_task(task_id):
    """Завершает задание"""
    # Получаем задание
    response = supabase.table('tasks').select('*').eq('id', task_id).execute()
    if not response.data:
        return False
    
    task = response.data[0]
    
    if task['status'] != 'in_progress':
        return False
    
    # Обновляем статус
    supabase.table('tasks').update({'status': 'completed'}).eq('id', task_id).execute()
    
    # Выдаем награду
    if task['assigned_to']:
        user_id = task['assigned_to']
        add_coins(user_id, task['reward_coins'])
        add_exp(user_id, task['reward_exp'])
    
    return True

# ========== СООБЩЕНИЯ АДМИНУ ==========

def save_message_to_admin(user_id, message_type, text):
    """Сохраняет сообщение для админа"""
    msg_data = {
        'user_id': user_id,
        'type': message_type,
        'text': text,
        'status': 'pending'
    }
    response = supabase.table('messages_to_admin').insert(msg_data).execute()
    
    # Увеличиваем счетчик сообщений
    user = get_user(user_id)
    if user:
        supabase.table('users').update({
            'messages_sent': user.get('messages_sent', 0) + 1
        }).eq('user_id', user_id).execute()
    
    return response.data[0]['id'] if response.data else 0

def get_messages_to_admin():
    """Получает все сообщения для админа"""
    response = supabase.table('messages_to_admin').select('*, users!inner(nickname, username)').eq('status', 'pending').execute()
    return response.data if response.data else []

def get_message(msg_id):
    """Получает сообщение по ID"""
    response = supabase.table('messages_to_admin').select('*, users!inner(nickname, username)').eq('id', msg_id).execute()
    if response.data:
        msg = response.data[0]
        msg['user'] = {
            'nickname': msg['users']['nickname'],
            'username': msg['users']['username'],
            'user_id': msg['user_id']
        }
        del msg['users']
        return msg
    return None

def update_message_status(msg_id, status):
    """Обновляет статус сообщения"""
    response = supabase.table('messages_to_admin').update({
        'status': status
    }).eq('id', msg_id).execute()
    return bool(response.data)

# ========== РАБОТЫ И КАТЕГОРИИ ==========

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
    response = supabase.table('users').select('*').execute()
    if not response.data:
        return 0
    
    count = 0
    for user in response.data:
        if job_name in user.get('selected_jobs', []):
            count += 1
    return count

def is_job_available(job_name):
    """Проверяет доступность работы"""
    if job_name not in JOBS_DETAILS:
        return False
    
    max_users = JOBS_DETAILS[job_name]['max_users']
    current_users = get_users_count_by_job(job_name)
    
    return current_users < max_users

# Инициализируем админа при импорте
initialize_admin()
