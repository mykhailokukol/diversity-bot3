from pymongo import MongoClient
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler, CallbackContext

from bot.services import (
    get_exchange_rate,
    get_participants_number,
    add_user_to_db,
    already_participant,
)
from bot.config import settings

WINNER = 0


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    client = MongoClient(settings.MONGODB_CLIENT_URL)

    if already_participant(client, update):
        await update.message.reply_text("Вы уже участвуете в розыгрыше.")
        return

    X = get_participants_number(client)
    S = await get_exchange_rate()
    N = (X + 100) * S
    add_user_to_db(client, update, N)

    await update.message.reply_text(
        f"Отлично!\nВы участвуете в розыгрыше приза!\nВаш номер в розыгрыше: {N}"
    )


async def choose_winner(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    if int(update.message.from_user.id) != int(settings.MODERATOR_ID):
        return

    client = MongoClient(settings.MONGODB_CLIENT_URL)
    db = client["ski-bot"]
    participants = db["participants"]
    participants_keyboard = [[]]

    for participant in participants.find({}):
        participants_keyboard[0].append(InlineKeyboardButton(participant["win_number"]))
    markup = ReplyKeyboardMarkup(participants_keyboard)
    await update.message.reply_text(
        "Выберите победителя или введите номер выиграшного билета вручную:",
        reply_markup=markup,
    )

    return WINNER


async def send_congratulations(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> ConversationHandler.END:
    win_number = int(update.message.text)
    client = MongoClient(settings.MONGODB_CLIENT_URL)
    db = client["ski-bot"]
    participants = db["participants"]
    winner = participants.find_one({"win_number": win_number})

    keyboard = [
        [
            InlineKeyboardButton(
                "Подтвердить", callback_data=f"approve_{winner['win_number']}"
            ),
            InlineKeyboardButton(
                "Отказаться", callback_data=f"reject_{winner['win_number']}"
            ),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=winner["user_id"],
        text="Поздавляем, Вы выиграли приз!\n"
        'Чтобы получить его, подтвердите это нажав на кнопку "Подтвердить".\n'
        'Или откажитесь нажав на "Отказаться"',
        reply_markup=markup,
    )
    return ConversationHandler.END


async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """No description needed"""
    return ConversationHandler.END


async def callback(
    update: Update,
    context: CallbackContext,
) -> None:
    query = update.callback_query
    answer = await query.answer()

    if answer:
        if "approve_" in query.data:
            win_number = query.data.split("_")[1]
            await context.bot.send_message(
                chat_id=settings.MODERATOR_ID,
                text=f"Пользователь с номером {win_number} подтвердил получение приза.",
            )
        if "reject_" in query.data:
            win_number = query.data.split("_")[1]
            await context.bot.send_message(
                chat_id=settings.MODERATOR_ID,
                text=f"Пользователь с номером {win_number} отказался от получения приза.",
            )
