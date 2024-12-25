import logging
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

# Ініціалізація роутера
router = Router()

ADMIN_IDS = [1332517469, 6395768505]  # Додано ще одного адміністратора

# Логування
logging.basicConfig(level=logging.INFO)

# Обробка команди /help
@router.message(Command("help"))
async def help_command(message: Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username or "(без юзернейму)"
    
    # Перевірка наявності тексту проблеми після команди
    user_text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    if not user_text:
        await message.answer("Будь ласка, додайте текст проблеми після команди /help.")
        return

    # Формування повідомлення для адміністратора
    admin_message = (
        f"Нове повідомлення від користувача:\n\n"
        f"👤 ID користувача: {user_id}\n"
        f"🔑 Нік користувача: @{username}\n"
        f"💬 Повідомлення: {user_text}"
    )

    # Відправка адміну
    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, admin_message)

    # Відповідь користувачу
    await message.answer("Ваше повідомлення успішно відправлено адміну. Дякуємо!")

# Обробка команди /reply для відповіді користувачеві
@router.message(Command("reply"))
async def reply_command(message: Message, bot: Bot):
    # Перевірка на права доступу
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Ця команда доступна лише адміністраторам.")
        return

    # Очікуємо формат: /reply <ID користувача> <текст відповіді>
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Невірний формат команди. Використовуйте: /reply <ID користувача> <текст>")
        return

    try:
        user_id = int(parts[1])  # ID користувача
        reply_text = parts[2]    # Текст відповіді

        # Надсилаємо повідомлення користувачу
        await bot.send_message(user_id, f"Відповідь від адміністратора:\n\n{reply_text}")
        await message.answer("Повідомлення успішно надіслано користувачу.")
    except Exception as e:
        await message.answer(f"Помилка при відправці повідомлення: {e}")
        logging.error(f"Помилка: {e}")

