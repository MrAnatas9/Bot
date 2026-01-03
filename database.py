import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from supabase import create_client, Client
from config import *

# Инициализация Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== ОПИСАНИЯ РАБОТ ==========
JOBS_DETAILS: Dict[str, Dict] = {
    "👑 Судья": {"category": "🏛️ Управление", "min_level": 1, "max_users": 2},
    "⚖️ Адвокат": {"category": "🏛️ Управление", "min_level": 1, "max_users": 4},
    "🔍 Следователь": {"category": "🏛️ Управление", "min_level": 1, "max_users": 2},
    "🕊️ Дипломат": {"category": "🏛️ Управление", "min_level": 1, "max_users": 2},
    "📜 Архивариус": {"category": "🏛️ Управление", "min_level": 1, "max_users": 2},
    "🛡️ Офицер Безопасности": {"category": "🏛️ Управление", "min_level": 1, "max_users": 2},
    "🎥 Ютубер": {"category": "📢 Медиа", "min_level": 1, "max_users": 2},
    "📰 Журналист": {"category": "📢 Медиа", "min_level": 1, "max_users": 3},
    "✍️ Писатель": {"category": "📢 Медиа", "min_level": 1, "max_users": 5},
    "🎨 Художник": {"category": "📢 Медиа", "min_level": 1, "max_users": 4},
    "📢 Рекламист": {"category": "📢 Медиа", "min_level": 1, "max_users": 3},
    "🎙️ Ведущий": {"category": "📢 Медиа", "min_level": 1, "max_users": 3},
    "📱 SMM-менеджер": {"category": "📢 Медиа", "min_level": 1, "max_users": 2},
    "💻 Программист": {"category": "⚙️ Разработка", "min_level": 1, "max_users": 3},
    "🔨 Мастер": {"category": "⚙️ Разработка", "min_level": 1, "max_users": 3},
    "🎬 Монтажёр": {"category": "⚙️ Разработка", "min_level": 1, "max_users": 2},
    "🏗️ Строитель": {"category": "⚙️ Разработка", "min_level": 1, "max_users": 5},
    "📊 Оператор": {"category": "⚙️ Разработка", "min_level": 1, "max_users": 2},
    "🎮 Тестировщик": {"category": "⚙️ Разработка", "min_level": 1, "max_users": 2},
    "📐 Архитектор": {"category": "⚙️ Разработка", "min_level": 1, "max_users": 3},
    "👁️ Куратор": {"category": "📚 Поддержка", "min_level": 1, "max_users": 5},
    "📖 Историк": {"category": "📚 Поддержка", "min_level": 1, "max_users": 2},
    "🧭 Гид": {"category": "📚 Поддержка", "min_level": 1, "max_users": 2},
    "🤝 Психолог": {"category": "📚 Поддержка", "min_level": 1, "max_users": 2},
    "🏹 Разведчик": {"category": "🎭 Оборона", "min_level": 1, "max_users": 2}
}

# ========== СЛУЖЕБНЫЕ ФУНКЦИИ ==========
def initialize_database() -> None:
    """Инициализация базы данных при первом запуске"""
    # Проверяем наличие админа
    admin = get_user(ADMIN_ID)
    if not admin:
        admin_data = {
            'user_id': ADMIN_ID,
            'username': 'admin',
            'nickname': '👑 Глава Клана',
            'job': '👑 Глава Клана',
            'selected_jobs': ['👑 Глава Клана'],
            'coins': 999999,
            'level': 10,
            'exp': 0,
            'messages_sent': 0,
            'is_admin': True,
            'debt': 0,
            'registration_date': datetime.now().isoformat()
        }
        supabase.table('users').insert(admin_data).execute()
        print("✅ Админ инициализирован")

# ========== ФУНКЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========
def save_user(user_id: int, username: str, nickname: str, selected_jobs: List[str]) -> bool:
    """Создает/обновляет пользователя"""
    try:
        user_data = {
            'user_id': user_id,
            'username': username,
            'nickname': nickname,
            'job': selected_jobs[0] if selected_jobs else 'Безработный',
            'selected_jobs': selected_jobs,
            'coins': START_COINS,
            'level': 1,
            'exp': 0,
            'messages_sent': 0,
            'is_admin': False,
            'debt': 0,
            'registration_date': datetime.now().isoformat()
        }
        
        response = supabase.table('users').upsert(user_data).execute()
        return bool(response.data)
    except Exception as e:
        print(f"❌ Ошибка сохранения пользователя: {e}")
        return False

def get_user(user_id: int) -> Optional[Dict]:
    """Получает информацию о пользователе"""
    try:
        response = supabase.table('users').select('*').eq('user_id', user_id).execute()
        return response.data[0] if response.data else None
    except:
        return None

def get_all_users() -> List[Dict]:
    """Получает всех пользователей"""
    try:
        response = supabase.table('users').select('*').execute()
        return [user for user in response.data if not user.get('is_admin', False)]
    except:
        return []

def update_user_nickname(user_id: int, new_nickname: str) -> bool:
    """Обновляет никнейм пользователя"""
    try:
        response = supabase.table('users').update({'nickname': new_nickname}).eq('user_id', user_id).execute()
        return bool(response.data)
    except:
        return False

def update_user_jobs(user_id: int, selected_jobs: List[str]) -> bool:
    """Обновляет работы пользователя"""
    try:
        user_data = {
            'selected_jobs': selected_jobs,
            'job': selected_jobs[0] if selected_jobs else 'Безработный'
        }
        response = supabase.table('users').update(user_data).eq('user_id', user_id).execute()
        return bool(response.data)
    except:
        return False

# ========== ЭКОНОМИКА И ПЕРЕВОДЫ ==========
def transfer_coins(from_user_id: int, to_user_id: int, amount: int, reason: str = "") -> Tuple[bool, str]:
    """Переводит акойны между пользователями"""
    try:
        from_user = get_user(from_user_id)
        to_user = get_user(to_user_id)
        
        if not from_user or not to_user:
            return False, "Пользователь не найден"
        
        if amount <= 0:
            return False, "Сумма должна быть положительной"
        
        # Проверяем баланс (можно уходить в минус, но не больше MAX_DEBT)
        if from_user['coins'] - amount < -MAX_DEBT:
            return False, f"Превышен максимальный долг ({-MAX_DEBT} акойнов)"
        
        # Списание у отправителя
        supabase.table('users').update({'coins': from_user['coins'] - amount}).eq('user_id', from_user_id).execute()
        
        # Зачисление получателю
        supabase.table('users').update({'coins': to_user['coins'] + amount}).eq('user_id', to_user_id).execute()
        
        # Запись транзакции
        transaction_data = {
            'from_user_id': from_user_id,
            'to_user_id': to_user_id,
            'amount': amount,
            'reason': reason,
            'created_at': datetime.now().isoformat()
        }
        supabase.table('transactions').insert(transaction_data).execute()
        
        return True, f"Перевод {amount} акойнов выполнен"
    except Exception as e:
        return False, f"Ошибка перевода: {str(e)}"

def get_user_balance(user_id: int) -> int:
    """Получает баланс пользователя"""
    user = get_user(user_id)
    return user['coins'] if user else 0

def add_coins(user_id: int, amount: int, reason: str = "") -> bool:
    """Добавляет акойны пользователю"""
    try:
        user = get_user(user_id)
        if not user:
            return False
        
        new_balance = user['coins'] + amount
        response = supabase.table('users').update({'coins': new_balance}).eq('user_id', user_id).execute()
        
        if reason:
            transaction_data = {
                'from_user_id': 0,  # Система
                'to_user_id': user_id,
                'amount': amount,
                'reason': reason,
                'created_at': datetime.now().isoformat()
            }
            supabase.table('transactions').insert(transaction_data).execute()
        
        return bool(response.data)
    except:
        return False

def remove_coins(user_id: int, amount: int, reason: str = "") -> bool:
    """Снимает акойны у пользователя"""
    return add_coins(user_id, -amount, reason)

# ========== ОПЫТ И УРОВНИ ==========
def add_exp(user_id: int, amount: int) -> Tuple[bool, int]:
    """Добавляет опыт пользователю и проверяет повышение уровня"""
    try:
        user = get_user(user_id)
        if not user:
            return False, 0
        
        new_exp = user['exp'] + amount
        new_level = user['level']
        leveled_up = False
        
        # Проверяем повышение уровня
        while new_exp >= new_level * EXP_PER_LEVEL:
            new_exp -= new_level * EXP_PER_LEVEL
            new_level += 1
            leveled_up = True
            
            # Награда за уровень
            supabase.table('users').update({
                'coins': user['coins'] + LEVEL_UP_COINS
            }).eq('user_id', user_id).execute()
        
        # Обновляем опыт и уровень
        update_data = {
            'exp': new_exp,
            'level': new_level
        }
        supabase.table('users').update(update_data).eq('user_id', user_id).execute()
        
        return leveled_up, new_level
    except:
        return False, 0

def give_level(user_id: int, levels: int = 1) -> bool:
    """Повышает уровень пользователя напрямую"""
    try:
        user = get_user(user_id)
        if not user:
            return False
        
        new_level = user['level'] + levels
        response = supabase.table('users').update({'level': new_level}).eq('user_id', user_id).execute()
        return bool(response.data)
    except:
        return False

# ========== ЗАДАНИЯ ==========
def create_task(title: str, description: str, reward_coins: int, reward_exp: int) -> int:
    """Создает новое задание"""
    try:
        deadline = datetime.now() + timedelta(hours=TASK_DEADLINE_HOURS)
        task_data = {
            'title': title,
            'description': description,
            'reward_coins': reward_coins,
            'reward_exp': reward_exp,
            'status': 'active',  # active, assigned, completed, expired, rejected
            'deadline': deadline.isoformat(),
            'assigned_to': None,
            'created_at': datetime.now().isoformat()
        }
        response = supabase.table('tasks').insert(task_data).execute()
        return response.data[0]['id'] if response.data else 0
    except:
        return 0

def get_task(task_id: int) -> Optional[Dict]:
    """Получает информацию о задании"""
    try:
        response = supabase.table('tasks').select('*').eq('id', task_id).execute()
        return response.data[0] if response.data else None
    except:
        return None

def get_active_tasks() -> List[Dict]:
    """Получает активные задания"""
    try:
        response = supabase.table('tasks').select('*').eq('status', 'active').execute()
        return response.data if response.data else []
    except:
        return []

def get_user_tasks(user_id: int) -> List[Dict]:
    """Получает задания пользователя"""
    try:
        response = supabase.table('tasks').select('*').eq('assigned_to', user_id).execute()
        return response.data if response.data else []
    except:
        return []

def assign_task(task_id: int, user_id: int) -> Tuple[bool, str]:
    """Назначает задание пользователю"""
    try:
        task = get_task(task_id)
        if not task:
            return False, "Задание не найдено"
        
        if task['status'] != 'active':
            return False, "Задание недоступно"
        
        if task['assigned_to']:
            return False, "Задание уже взято"
        
        # Обновляем задание
        update_data = {
            'status': 'assigned',
            'assigned_to': user_id,
            'assigned_at': datetime.now().isoformat()
        }
        supabase.table('tasks').update(update_data).eq('id', task_id).execute()
        
        return True, "Задание успешно взято"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def submit_task_proof(task_id: int, user_id: int, proof_text: str = "") -> Tuple[bool, str]:
    """Отправляет proof выполнения задания"""
    try:
        task = get_task(task_id)
        if not task or task['assigned_to'] != user_id:
            return False, "Задание не найдено или не ваше"
        
        if task['status'] != 'assigned':
            return False, "Задание не в процессе выполнения"
        
        # Обновляем статус задания
        update_data = {
            'status': 'proof_submitted',
            'proof_text': proof_text,
            'proof_submitted_at': datetime.now().isoformat()
        }
        supabase.table('tasks').update(update_data).eq('id', task_id).execute()
        
        return True, "Proof отправлен на проверку"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def approve_task(task_id: int) -> Tuple[bool, str]:
    """Одобряет выполнение задания"""
    try:
        task = get_task(task_id)
        if not task or task['status'] != 'proof_submitted':
            return False, "Задание не на проверке"
        
        user_id = task['assigned_to']
        
        # Выдаем награду
        add_coins(user_id, task['reward_coins'], f"Награда за задание: {task['title']}")
        add_exp(user_id, task['reward_exp'])
        
        # Обновляем статус задания
        supabase.table('tasks').update({
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        }).eq('id', task_id).execute()
        
        return True, f"Задание одобрено! Награда: {task['reward_coins']} акойнов + {task['reward_exp']} опыта"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def reject_task(task_id: int, reason: str) -> Tuple[bool, str]:
    """Отклоняет proof задания"""
    try:
        task = get_task(task_id)
        if not task or task['status'] != 'proof_submitted':
            return False, "Задание не на проверке"
        
        user_id = task['assigned_to']
        
        # Штраф за невыполнение
        penalty = int(task['reward_coins'] * TASK_PENALTY_PERCENT)
        remove_coins(user_id, penalty, f"Штраф за невыполнение задания: {task['title']}")
        
        # Обновляем статус задания
        supabase.table('tasks').update({
            'status': 'rejected',
            'rejection_reason': reason,
            'rejected_at': datetime.now().isoformat()
        }).eq('id', task_id).execute()
        
        return True, f"Задание отклонено. Штраф: {penalty} акойнов"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def check_expired_tasks() -> None:
    """Проверяет просроченные задания и накладывает штрафы"""
    try:
        now = datetime.now()
        response = supabase.table('tasks').select('*').eq('status', 'assigned').execute()
        
        for task in response.data:
            deadline = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
            if now > deadline:
                user_id = task['assigned_to']
                
                # Штраф за просрочку
                penalty = int(task['reward_coins'] * TASK_PENALTY_PERCENT)
                remove_coins(user_id, penalty, f"Штраф за просрочку задания: {task['title']}")
                
                # Обновляем статус задания
                supabase.table('tasks').update({
                    'status': 'expired',
                    'expired_at': now.isoformat()
                }).eq('id', task['id']).execute()
    except Exception as e:
        print(f"❌ Ошибка проверки просроченных заданий: {e}")

# ========== РАБОТЫ ==========
def get_categories() -> List[str]:
    """Получает все категории работ"""
    categories = set()
    for job_details in JOBS_DETAILS.values():
        categories.add(job_details['category'])
    return list(categories)

def get_jobs_by_category(category: str) -> Dict[str, Dict]:
    """Получает работы по категории"""
    return {name: details for name, details in JOBS_DETAILS.items() 
            if details['category'] == category}

def get_users_count_by_job(job_name: str) -> int:
    """Считает количество пользователей с определенной работой"""
    try:
        response = supabase.table('users').select('selected_jobs').execute()
        count = 0
        for user in response.data:
            if job_name in user.get('selected_jobs', []):
                count += 1
        return count
    except:
        return 0

def is_job_available(job_name: str) -> bool:
    """Проверяет доступность работы"""
    if job_name not in JOBS_DETAILS:
        return False
    
    max_users = JOBS_DETAILS[job_name]['max_users']
    current_users = get_users_count_by_job(job_name)
    
    return current_users < max_users

# ========== СИСТЕМА УВОЛЬНЕНИЙ ==========
def fire_user(user_id: int, reason: str = "") -> Tuple[bool, str]:
    """Увольняет пользователя (снимает все работы)"""
    try:
        user = get_user(user_id)
        if not user:
            return False, "Пользователь не найден"
        
        # Снимаем все работы
        update_user_jobs(user_id, [])
        
        # Запись в логи
        if reason:
            log_data = {
                'action': 'fire',
                'user_id': user_id,
                'reason': reason,
                'admin_id': ADMIN_ID,
                'created_at': datetime.now().isoformat()
            }
            supabase.table('admin_logs').insert(log_data).execute()
        
        return True, f"Пользователь {user['nickname']} уволен"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

# ========== ГРУППОВЫЕ КОМАНДЫ ==========
def process_group_command(command: str, from_user_id: int, target_user_id: int = None, amount: int = None) -> Tuple[bool, str]:
    """Обрабатывает команды из группы"""
    try:
        if command == "забрать" and amount and target_user_id:
            return transfer_coins(target_user_id, from_user_id, amount, "Забрать в группе")
        
        elif command == "выдать" and amount and target_user_id:
            return transfer_coins(from_user_id, target_user_id, amount, "Выдать в группе")
        
        elif command == "уволить" and target_user_id:
            return fire_user(target_user_id, "Уволен через группу")
        
        else:
            return False, "Неизвестная команда или недостаточно параметров"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

# ========== ИНИЦИАЛИЗАЦИЯ ==========
# Создаем таблицы при первом импорте
try:
    initialize_database()
    print("✅ База данных инициализирована")
except Exception as e:
    print(f"❌ Ошибка инициализации базы: {e}")
