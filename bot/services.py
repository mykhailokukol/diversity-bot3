from random import randint

from aiohttp import ClientSession
from pymongo import MongoClient
from telegram import Update

from bot.config import settings


def get_first_two_numbers_after_period(number: float):
    number_str = str(number)
    period_index = number_str.find(".")
    if period_index == -1:
        raise ValueError("Number is not float (no period found)")
    numbers_after_period = number_str[period_index + 1 :]
    return int(numbers_after_period[:2])


async def get_exchange_rate():
    try:
        async with ClientSession() as session:
            async with session.get(
                f"https://api.freecurrencyapi.com/v1/latest"
                f"?currencies=RUB&base_currency=USD&apikey={settings.EXCHANGE_RATE_API_TOKEN}"
            ) as response:
                response = await response.json()
                response = get_first_two_numbers_after_period(response["data"]["RUB"])
                return response
    except Exception as e:
        print(f"Error occured on getting exchange rates:\n{e}")
        return randint(10, 99)


def get_participants_number(client: MongoClient) -> int:
    db = client["ski-bot"]
    participants = db["participants"]
    count = participants.count_documents({})
    return count + 1


def add_user_to_db(client: MongoClient, update: Update, win_number: int) -> None:
    db = client["ski-bot"]
    participants = db["participants"]

    participants.insert_one(
        {
            "user_id": update.message.from_user.id,
            "win_number": win_number,
        }
    )
    return True


def already_participant(client: MongoClient, update: Update):
    db = client["ski-bot"]
    participants = db["participants"]
    if participants.find_one({"user_id": update.message.from_user.id}):
        return True
    return False
