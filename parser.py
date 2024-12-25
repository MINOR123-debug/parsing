import json
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

async def initiate_parsing(client, channel_id, output_file="subscribers.json"):
    """
    Ініціює парсинг підписників вибраного каналу або чату та зберігає їх у JSON-файл.
    """
    subscribers = []
    try:
        offset = 0
        limit = 200  # Максимальна кількість учасників за один запит

        while True:
            participants = await client(GetParticipantsRequest(
                channel=channel_id,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))

            # Додаємо отриманих учасників до списку
            subscribers.extend([{"id": user.id, "username": user.username or "", "name": f"{user.first_name or ''} {user.last_name or ''}".strip()} for user in participants.users])

            # Якщо більше немає учасників, виходимо з циклу
            if len(participants.users) < limit:
                break

            offset += len(participants.users)

        # Зберігаємо підписників у JSON-файл
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(subscribers, file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Помилка під час парсингу підписників: {e}")

    return len(subscribers)  # Повертаємо кількість отриманих підписників
