import json
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
# Створення нового маршрутизатора
creit_router = Router()

# Шлях до файлу зі збереженими підписниками
SUBSCRIBERS_FILE = "subscribers.json"


def read_subscribers():
    try:
        # Відкриваємо файл subscribers.json і читаємо дані
        with open("subscribers.json", "r", encoding="utf-8") as file:
            subscribers = json.load(file)

            # Перевіряємо, чи дані у форматі списку
            if isinstance(subscribers, list):
                return subscribers
            else:
                print("Помилка формату: Очікується список підписників.")
                return []
    except FileNotFoundError:
        print("Файл subscribers.json не знайдений.")
        return []
    except json.JSONDecodeError:
        print("Помилка при зчитуванні JSON.")
        return []


# Функція для очищення списку підписників
def clear_subscribers():
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as file:
        json.dump([], file)


# Список адміністраторів
ADMINS = [1332517469, 7689890294]  # Замініть на реальні ID адміністраторів

# Команда для виведення підписників
@creit_router.message(Command("piplist"))
async def command_piplist(message: Message):
    # Перевірка доступу
    if message.from_user.id not in ADMINS:
        await message.answer("У вас немає прав доступу до цієї команди. ❌")
        return

    # Читаємо список підписників з файлу
    subscribers = read_subscribers()

    # Якщо список порожній
    if not subscribers:
        await message.answer("Список підписників порожній або файл не знайдений.")
        return

    # Ліміт у 4000 символів для Telegram повідомлення
    char_limit = 4000
    current_message = ""
    
    # Логування кількості підписників
    print(f"Знайдено {len(subscribers)} підписників.")

    for subscriber in subscribers:
        # Отримуємо ID, username та name
        user_id = subscriber.get("id", "Невідомий ID")
        username = subscriber.get("username", "Без username")
        name = subscriber.get("name", "Без імені")

        # Форматуємо рядок для виведення
        formatted_message = f"ID: {user_id}\n@{username}\n{name}\n\n"

        # Перевірка ліміту символів перед відправкою
        if len(current_message) + len(formatted_message) <= char_limit:
            current_message += formatted_message
        else:
            # Надсилаємо частину повідомлення, якщо перевищено ліміт
            await message.answer(current_message)
            current_message = formatted_message

    # Надсилаємо залишок, якщо він є
    if current_message:
        await message.answer(current_message)

    # Повідомлення про завершення
    await message.answer("Всі підписники видані.")


# Команда /clear - Очищає список підписників
@creit_router.message(Command("clear"))
async def command_clear(message: Message):
    # Перевірка доступу
    if message.from_user.id not in ADMINS:
        await message.answer("У вас немає прав доступу до цієї команди. ❌")
        return

    # Очищуємо список підписників
    clear_subscribers()
    await message.answer("Список підписників очищено!")
