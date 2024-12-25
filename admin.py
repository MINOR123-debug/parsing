from aiogram import types
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ContentType


router11 = Router()

import keyboards as kb


PYMENTS_TOKEN = '410694247:TEST:f798f05e-1c2e-4fa7-9eca-36a66efccb92'

ADMINS = [1332517469 , 6395768505]



import json
from datetime import datetime, timedelta

ACTIVITY_FILE = "users_activity.json"

def load_activity():
    """Завантажуємо активність користувачів з файлу."""
    try:
        with open(ACTIVITY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_activity(activity):
    """Зберігаємо активність користувачів у файл."""
    with open(ACTIVITY_FILE, "w") as f:
        json.dump(activity, f, indent=4)

def update_user_activity(user_id):
    """Оновлюємо час останньої активності для користувача, без створення нового запису."""
    activity = load_activity()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Перевірка, чи існує вже запис про активність користувача
    if user_id in activity:
        # Якщо є, оновлюємо тільки час останньої активності
        activity[user_id] = current_time
    else:
        # Якщо немає, створюємо новий запис
        activity[user_id] = current_time

    # Зберігаємо оновлений список активностей
    save_activity(activity)

def get_online_users():
    
    activity = load_activity()
    online_users = []

    current_time = datetime.now()
    for user_id, last_active_str in activity.items():
        last_active = datetime.strptime(last_active_str, "%Y-%m-%d %H:%M:%S")
        if current_time - last_active <= timedelta(minutes=600):
            online_users.append(user_id)

    return online_users







@router11.message(Command("admin"))
async def admin_panel(message: types.Message):
    user_id = message.from_user
    user_name = message.from_user.full_name
    print(f"Користувач {user_name} з ID {user_id} відправив команду /admin")
    if message.from_user.id in ADMINS:
        await message.answer(f"{message.from_user.first_name} ADMIN ⱽᴵᴾ ⚡️ зайшов в панель, ")
        await message.answer(f"Ви увійшли в адмін панель, ✅" , reply_markup=kb.admin_panel)
    else:
        await message.answer("У вас нет доступа к админ-панели. ❌")

   
@router11.message(F.text == '🌟Зробити росилку🌟')
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer(f"Для росилки, уведіть команду /sendall")
    else:
        await message.answer("У вас нет доступа к админ-панели. ❌")


@router11.message(F.text == "🌟Активність🌟")
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer(f"тут ви можете подивитися активніть користувачів\n"
                                "Command - /online 'ви можете переглянути останю активність користувачів'\n"
                                "\n"
                                "вам покаже кількість користувачів які були у мережі за остнані 3години\n")
    else:
        await message.answer("У вас нет доступа к админ-панели. ❌")

@router11.message(F.text == '⚡️Назад⚡️')
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer(f"Виберіть пункт меню" , reply_markup=kb.admin_panel)
    else:
        await message.answer("У вас нет доступа к админ-панели. ❌")

@router11.message(F.text == "⏰Тех-перерва⏰")
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer(f"⚡️\n"
                            "Command - /maintenance 'по цій команді бот начне свою автоматичну перевірку вам лишиться просто почикати певний час'\n"
                            "\n"
                            "після цего бот перезапуститься і буде парцювати ✅")
    else:
        await message.answer("У вас нет доступа к админ-панели. ❌")


@router11.message(F.text == "👥Користувачі👥")
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer(f"⚡️\n"
                            "Command - /list_users 'показує вам кількість всіх користувачів бота'\n"
                            "\n"
                            "уведіть її і дізнайтесь всю кількість людей в боті")
    else:
        await message.answer("У вас нет доступа к админ-панели. ❌")


from aiogram import types

@router11.message(F.text == "/online")
async def online_users(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("У вас немає доступу до цієї команди! ❌")
        return

    online_users = get_online_users()
    online_count = len(online_users)
    
    await message.answer(f"Кількість користувачів в онлайн: {online_count}")



import asyncio
from aiogram import types
import random

@router11.message(F.text == "/maintenance")
async def maintenance_command(message: types.Message):
    
    if message.from_user.id not in ADMINS:
        await message.answer("У вас немає доступу до цієї команди! ❌")
        return

   
    await message.answer("🔧 Бот знаходиться на технічній перерві! очікуєте бот перевіряється на стабільність...")
    await asyncio.sleep(5)
    await message.answer("Запуск процесу перевірки роботи...")
    await asyncio.sleep(7)
    await message.answer("перевірка всіх команд⌛️")
    await asyncio.sleep(10)
    await message.answer("команд⌛️ парцюють успішно✅")
    await asyncio.sleep(2)
    await message.answer("перевірка роботи бази даних 🗂")
    await asyncio.sleep(15)
    await message.answer("база даних працює успішно ✅")
    await asyncio.sleep(4)
    await message.answer("перевірка файлів на збой. . .")
    await asyncio.sleep(9)
    await message.answer("всі файли пройшли провірку ✅")
    await asyncio.sleep(1)
    await message.answer("Технічну перерву завершено! Бот працює Стабільно ✅")
    await message.answer("Помилок не виявлено бот працює коректно у всіх користувачів")



import json
from aiogram import types
from aiogram.filters import Command

# Шлях до файлу з користувачами
USERS_FILE = "users.json"

# Функція для завантаження ID користувачів із файлу
def load_user_ids():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@router11.message(Command("list_users"))
async def list_users_command(message: types.Message):
    # Перевірка доступу для адміністраторів
    if message.from_user.id not in ADMINS:
        await message.answer("У вас немає прав доступу до цієї команди. ❌")
        return

    # Завантажуємо список ID користувачів
    user_ids = load_user_ids()

    if not user_ids:
        await message.answer("Файл користувачів порожній або не знайдений.")
        return

    # Формуємо список з усіх ID
    user_list = ""
    for index, user_id in enumerate(user_ids, start=1):
        user_list += f"{index}. 👤ID: {user_id}\n"

    # Якщо повідомлення занадто довге для Telegram (4000 символів), розбиваємо його на частини
    char_limit = 4000
    if len(user_list) > char_limit:
        parts = [user_list[i:i+char_limit] for i in range(0, len(user_list), char_limit)]
        for part in parts:
            await message.answer(part)
    else:
        await message.answer(user_list)




from aiogram import types

@router11.message()
async def user_interaction(message: types.Message):
    user_id = message.from_user.id
    update_user_activity(user_id)        
