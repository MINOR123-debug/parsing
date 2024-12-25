import json
import os
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards import search_menu
from aiogram.filters import Command

command_router = Router()

# Шлях до файлу з даними користувачів
users_file = "users.json"

# Функція для збереження ID користувачів
def save_user_id(user_id):
    # Якщо файл існує, відкриваємо його та додаємо нового користувача
    if os.path.exists(users_file):
        with open(users_file, "r", encoding="utf-8") as file:
            users_data = json.load(file)
    else:
        # Якщо файлу немає, створюємо новий список
        users_data = []

    # Перевіряємо, чи є вже цей користувач в списку
    if user_id not in users_data:
        users_data.append(user_id)
        # Записуємо дані в файл
        with open(users_file, "w", encoding="utf-8") as file:
            json.dump(users_data, file, ensure_ascii=False, indent=4)

@command_router.message(CommandStart())
async def start_command(message: Message):
    """
    Обробник команди /start.
    """
    # Зберігаємо ID користувача
    save_user_id(message.from_user.id)
    
    await message.answer(
        f"Привіт, {message.from_user.first_name}! 👋\n\n"
        "Я тут, щоб допомогти тобі знайти Telegram-канали, групи чи чати, що відповідають твоєму запиту.🫵\n"
        "Просто напиши 💬 в чат @ParsingTOPbot або скористайся кнопкою нижче👇, щоб почати пошук!\n"
        "Не забудь закріпити мене в списку чатів для швидкого доступу! 🔥\n"
    )
    await message.answer(
        "Просто натисни кнопку нижче і ми одразу почнемо! 🚀",
        reply_markup=search_menu,
    )


# Список ID адміністраторів
ADMINS = [1332517469 , 6395768505] # Замість цих ID вставте реальні ID ваших адміністраторів

@command_router.message(Command("list"))
async def command_piplist(message: Message):
    # Перевірка чи користувач є адміном
    if message.from_user.id in ADMINS:
        await message.answer(
            "Command - /start 'запуск і перезапуск бота'\n"
            "\n"
            "Command - /help 'Підтримка в боті'\n"
            "\n"
            "Command - /sendall 'команда для розсилки-реклами'\n"
            "\n"
            "Command - /piplist 'видання підписників у списку'\n"
            "\n"
            "Command - /clear 'очищення списку підписників'\n"
            "\n"
            "Command - /reply 'відповідь на проблему тільки адмінам!'\n"
            "\n"
            "Command - /list 'подивитися список команди' \n"
            "\n"
            "Command - /admin 'адмін панель для легкого використання'\n"
            "\n"
        )
    else:
        await message.answer("У вас немає доступу до цієї команди. ❌")