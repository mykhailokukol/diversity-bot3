import random

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
        return random.randint(10, 99)


def get_participants_number(client: MongoClient) -> int:
    db = client["ski-bot"]
    participants = db["participants"]
    count = participants.count_documents({})
    return count + 1


def add_user_to_db(
    client: MongoClient, update: Update, win_number: int, resort: str
) -> None:
    db = client["ski-bot"]
    participants = db["participants"]

    participants.insert_one(
        {
            "user_id": update.message.from_user.id,
            "win_number": win_number,
            "resort": resort,
        }
    )


def already_participant(client: MongoClient, update: Update, resort: str) -> bool:
    db = client["ski-bot"]
    participants = db["participants"]
    if participants.find_one(
        {"user_id": update.message.from_user.id, "resort": resort}
    ):
        return True
    return False


def get_random_prize(client: MongoClient, update: Update, resort: str) -> str:
    db = client["ski-bot"]
    prizes = db["prizes"]
    prizes_list = list(
        prizes.find(
            {"resort": resort, "amount": {"$gt": 0}},
            {"_id": 0, "name": 1},
        )
    )
    if prizes_list:
        random_prize = random.choice(prizes_list)
        prizes.update_one(
            {"name": random_prize["name"], "resort": resort},
            {"$inc": {"amount": -1}},
        )
        return random_prize["name"]
    else:
        return "К сожалению, призов не осталось"
