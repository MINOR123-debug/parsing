from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, CallbackQuery
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import Channel, Chat
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
import uuid
import asyncio
from parser import initiate_parsing  # Імпортуємо функцію парсингу з parser.py
import json

# Параметри Telegram API
API_ID = 20979523
API_HASH = "e8aa8ee24dbe98293f5bd124071d4f56"
PHONE_NUMBER = "+380631776515"

# Ініціалізація Telethon клієнта
client = TelegramClient("search_session", API_ID, API_HASH)

# Створюємо роутер
inline_router = Router()

# Глобальні змінні для збереження останнього пошукового запиту і результатів
last_search_query = None
last_search_results = []


async def setup_telethon():
    """
    Ініціалізація та авторизація Telethon клієнта.
    """
    if not client.is_connected():
        await client.start(PHONE_NUMBER)
        print("Telethon успішно авторизовано!")


@inline_router.inline_query()
async def inline_query_handler(query: InlineQuery):
    global last_search_query, last_search_results

    search_query = query.query.strip().lower()
    results = []

    if not search_query:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="Введіть текст для пошуку",
                input_message_content=InputTextMessageContent(
                    message_text="Почніть вводити текст для пошуку."
                ),
                description="Введіть частину назви каналу, бота або чату."
            )
        )
    else:
        try:
            # Пошук через Telethon
            search_result = await client(SearchRequest(
                q=search_query,
                limit=200
            ))

            # Зберігаємо результати пошуку
            last_search_results = []

            # Обробка знайдених результатів через Telethon
            for entity in search_result.chats:
                if isinstance(entity, Channel) and entity.username:  # Публічні канали
                    username = entity.username
                    title = entity.title
                    subscribers = getattr(entity, 'participants_count', 'Невідомо')

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔍 Пошук", switch_inline_query_current_chat='')],
                        [InlineKeyboardButton(text="Парсити", callback_data=f"parse_{entity.id}")]
                    ])

                    result_text = (
                        f"Канал «{title}» (https://t.me/{username}) (@{username})\n"
                        f"{subscribers} підписників.\n"
                        f"Знайдено за допомогою @ParsingTOPbot"
                    )

                    last_search_results.append(
                        InlineQueryResultArticle(
                            id=str(uuid.uuid4()),
                            title=title,
                            input_message_content=InputTextMessageContent(
                                message_text=result_text
                            ),
                            description=f"{subscribers} підписників (канал).",
                            reply_markup=keyboard
                        )
                    )

                elif isinstance(entity, Chat):  # Чати
                    title = entity.title
                    participants = getattr(entity, 'participants_count', 'Невідомо')

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔍 Пошук", switch_inline_query_current_chat='')],
                        [InlineKeyboardButton(text="Парсити", callback_data=f"parse_{entity.id}")]
                    ])

                    result_text = (
                        f"Група або чат: {title}\n"
                        f"Учасників: {participants}.\n"
                        f"Знайдено за допомогою @ParsingTOPbot"
                    )

                    last_search_results.append(
                        InlineQueryResultArticle(
                            id=str(uuid.uuid4()),
                            title=title,
                            input_message_content=InputTextMessageContent(
                                message_text=result_text
                            ),
                            description=f"{participants} учасників (група/чат).",
                            reply_markup=keyboard
                        )
                    )

            # Відправка результатів
            await query.answer(last_search_results, cache_time=1, is_personal=True)

        except Exception as e:
            print(f"Помилка під час пошуку: {e}")
            last_search_results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="Помилка пошуку",
                    input_message_content=InputTextMessageContent(
                        message_text="Виникла помилка під час пошуку. Спробуйте ще раз."
                    ),
                    description="Спробуйте ще раз."
                )
            )

    # Відправляємо результати
    await query.answer(last_search_results, cache_time=1, is_personal=True)



from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

ADMINS = [1332517469 , 6395768505]

@inline_router.callback_query(F.data.startswith("parse_"))
async def callback_parse(callback: CallbackQuery):
    """
    Обробка кнопки "Парсити".
    """
    if callback.from_user.id not in ADMINS:
        # Якщо користувач не є адміністратором, відправляємо повідомлення і виходимо
        await callback.answer("У вас немає прав доступу до цієї функції. ❌", show_alert=True)
        return

    channel_id = int(callback.data.split("_")[1])  # Отримуємо ID вибраного каналу/групи
    output_file = f"subscribers.json"

    parsing_message = None  # Ініціалізація змінної для уникнення UnboundLocalError

    try:
        # Перевірка на наявність повідомлення в callback
        if callback.message:
            # Відправляємо повідомлення про початок парсингу
            parsing_message = await callback.message.answer("Парсимо учасників. Це може зайняти час...")
        else:
            print("callback.message відсутнє!")

        # Викликаємо функцію парсингу
        subscriber_count = await initiate_parsing(client, channel_id, output_file)

        if subscriber_count > 0:
            # Після завершення парсингу оновлюємо повідомлення про завершення
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text="Отримати список", callback_data=f"get_list_{channel_id}")
                ]]
            )

            if parsing_message:
                await parsing_message.edit_text(
                    f"Парсинг завершено! Знайдено {subscriber_count} підписників.",
                    reply_markup=keyboard
                )
            else:
                await callback.answer(f"Парсинг завершено! Знайдено {subscriber_count} підписників.", reply_markup=keyboard)

        else:
            # Якщо немає підписників (можливо, група пуста)
            if parsing_message:
                await parsing_message.edit_text(
                    "Парсинг завершено, але учасників не знайдено.",
                )
            else:
                await callback.answer("Парсинг завершено, але учасників не знайдено.")

    except Exception as e:
        # Якщо виникла помилка (наприклад, канал приватний або недоступний)
        error_message = "Не вдалося отримати підписників. Можливо, канал або група приватні."
        if parsing_message:
            await parsing_message.edit_text(error_message)
        else:
            await callback.answer(error_message)
        print(f"Помилка під час парсингу: {e}")










@inline_router.callback_query(F.data.startswith("get_list_"))
async def callback_get_list(callback: CallbackQuery):
    """
    Обробка кнопки "Отримати список".
    """
    channel_id = int(callback.data.split("_")[2])  # Отримуємо ID вибраного каналу/групи
    output_file = f"subscribers_{channel_id}.json"

    try:
        # Читаємо список підписників із JSON-файлу
        with open(output_file, "r", encoding="utf-8") as file:
            subscribers = json.load(file)

        # Розбиваємо список на частини для відправки
        CHUNK_SIZE = 50  # Ліміт учасників для одного повідомлення
        for i in range(0, len(subscribers), CHUNK_SIZE):
            chunk = subscribers[i:i + CHUNK_SIZE]
            chunk_message = "\n".join([f"{s['name']} (@{s['username']})" for s in chunk])

            if callback.message:
                await callback.message.answer(chunk_message)

        if callback.message:
            await callback.message.answer("Це всі підписники.")

    except FileNotFoundError:
        if callback.message:
            await callback.message.answer("Помилка: список підписників не знайдено.")