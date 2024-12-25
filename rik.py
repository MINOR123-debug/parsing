import sqlite3
import asyncio
import json
from aiogram import types, Router, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
# Роутер для адміністраторів
routeradm = Router()

# Список адміністраторів
ADMINS = [1332517469, 7689890294]

# Шлях до бази даних


JSON_PATH = "users.json"

# Станова машина
class BroadcastStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_media = State()
    waiting_for_button_text = State()
    waiting_for_button_url_or_profile = State()
    waiting_for_confirmation = State()

# Функція для перевірки адміністратора
async def is_admin(message: types.Message) -> bool:
    """Перевіряє, чи є користувач адміністратором."""
    return message.from_user.id in ADMINS



# Функція для отримання користувачів із JSON файлу
def get_users_from_json():
    """Отримує список користувачів із JSON файлу."""
    try:
        with open(JSON_PATH, "r") as file:
            users = json.load(file)
            if isinstance(users, list):  # Перевірка, чи це список
                return users
            else:
                return []
    except Exception as e:
        print(f"Помилка при зчитуванні з JSON файлу: {e}")
        return []


# Функція для збору користувачів
def get_all_users():
    """Об’єднує користувачів із бази та жорстко прописаного списку."""
    
    user_ids_from_json = get_users_from_json()
    user_ids_hardcoded = [
        
    ]
    return list(set(user_ids_from_json + user_ids_hardcoded))

# Хендлер для запуску створення розсилки
@routeradm.message(Command("sendall"))
async def start_broadcast_creation(message: types.Message, state: FSMContext):
    """Початок створення розсилки."""
    if not await is_admin(message):
        await message.answer("Ця команда доступна тільки адміністраторам!")
        return
    await state.set_state(BroadcastStates.waiting_for_text)
    await message.answer("Введіть текст для розсилки:")

# Хендлер для тексту
@routeradm.message(BroadcastStates.waiting_for_text)
async def get_broadcast_text(message: types.Message, state: FSMContext):
    """Зберігає текст для розсилки."""
    if not message.text:
        await message.answer("Будь ласка, введіть текст для розсилки!")
        return
    await state.update_data(text=message.text)
    await state.set_state(BroadcastStates.waiting_for_media)
    await message.answer("Додайте фото або відео для розсилки:")

# Хендлер для медіа
@routeradm.message(BroadcastStates.waiting_for_media)
async def get_broadcast_media(message: types.Message, state: FSMContext):
    """Зберігає фото або відео для розсилки."""
    media_type = None
    media_id = None

    if message.photo:
        media_type = "photo"
        media_id = message.photo[-1].file_id
    elif message.video:
        media_type = "video"
        media_id = message.video.file_id
    else:
        await message.answer("Будь ласка, надішліть фото або відео!")
        return

    await state.update_data(media_type=media_type, media_id=media_id)
    await state.set_state(BroadcastStates.waiting_for_button_text)
    await message.answer("Введіть текст для кнопки:")

# Хендлер для тексту кнопки
@routeradm.message(BroadcastStates.waiting_for_button_text)
async def get_button_text(message: types.Message, state: FSMContext):
    """Зберігає текст кнопки."""
    if not message.text:
        await message.answer("Будь ласка, введіть текст для кнопки!")
        return
    await state.update_data(button_text=message.text)
    await state.set_state(BroadcastStates.waiting_for_button_url_or_profile)
    await message.answer("Введіть посилання (http/https) або профіль Telegram (@username):")

# Хендлер для посилання або профілю Telegram
@routeradm.message(BroadcastStates.waiting_for_button_url_or_profile)
async def get_button_url_or_profile(message: types.Message, state: FSMContext):
    """Зберігає посилання або профіль для кнопки."""
    input_data = message.text.strip()

    # Якщо починається з @ — це профіль Telegram
    if input_data.startswith("@"):
        # Перевірка на коректний формат профілю Telegram
        username = input_data[1:]  # Видаляємо "@"
        if username.isalnum() or "_" in username:  # Перевірка: лише букви, цифри, підкреслення
            button_url = f"https://t.me/{username}"  # Формуємо правильне посилання
        else:
            await message.answer("Введіть коректний профіль Telegram у форматі @username (букви, цифри, підкреслення).")
            return
    # Якщо це звичайне посилання
    elif input_data.startswith("http://") or input_data.startswith("https://"):
        button_url = input_data
    else:
        await message.answer("Будь ласка, введіть коректне посилання (http/https) або профіль Telegram (@username):")
        return

    # Зберігаємо дані в стані
    await state.update_data(button_url=button_url)

    # Отримуємо всі дані
    data = await state.get_data()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=data["button_text"], url=data["button_url"]),
        ],
        [
            InlineKeyboardButton(text="Відправити", callback_data="send_broadcast"),
            InlineKeyboardButton(text="Скасувати", callback_data="cancel_broadcast")
        ]
    ])

    # Попередній перегляд розсилки
    if data["media_type"] == "photo":
        await message.answer_photo(
            photo=data["media_id"],
            caption=f"Текст: {data['text']}",
            reply_markup=markup
        )
    elif data["media_type"] == "video":
        await message.answer_video(
            video=data["media_id"],
            caption=f"Текст: {data['text']}",
            reply_markup=markup
        )

    # Перехід до наступного стану
    await state.set_state(BroadcastStates.waiting_for_confirmation)


@routeradm.callback_query()
async def handle_broadcast_action(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обробляє вибір дії: відправити чи скасувати."""
    data = await state.get_data()

    if callback.data == "send_broadcast":
        user_ids = get_all_users()  # Отримуємо список користувачів для розсилки

        for user_id in user_ids:  # Правильна ітерація по списку
            try:
                if data["media_type"] == "photo":
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=data["media_id"],
                        caption=f"Текст: {data['text']}",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text=data["button_text"], url=data["button_url"])]
                        ])
                    )
                elif data["media_type"] == "video":
                    await bot.send_video(
                        chat_id=user_id,
                        video=data["media_id"],
                        caption=f"Текст: {data['text']}",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text=data["button_text"], url=data["button_url"])]
                        ])
                    )
            except TelegramForbiddenError:
                print(f"Користувач {user_id} заблокував бота або видалив акаунт. Пропускаємо.")
                continue
            except TelegramBadRequest as e:
                print(f"Помилка BadRequest з користувачем {user_id}: {e}")
                continue
            except Exception as e:
                print(f"Інша помилка з користувачем {user_id}: {e}")
                continue

        await callback.message.answer("Розсилка завершена!")
        await state.clear()

    elif callback.data == "cancel_broadcast":
        # Видаляємо повідомлення попереднього перегляду
        try:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        except Exception as e:
            print(f"Не вдалося видалити повідомлення: {e}")

        # Очищаємо стан і повідомляємо про скасування
        await state.clear()
        await callback.message.answer("Розсилка скасована. Ви можете почати заново за допомогою команди /sendall.")
