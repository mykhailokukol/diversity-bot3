import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from bot.base import (
    RESORT,
    WINNER,
    WINNER_RESORT,
    callback,
    cancel,
    choose_resort,
    choose_winner,
    choose_winner_resort,
    send_congratulations,
    start,
)
from bot.config import settings

logging.basicConfig(
    format="%(levelname)s | %(name)s | %(asctime)s | %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)


def main() -> None:
    app = ApplicationBuilder().token(settings.TG_TOKEN).build()

    moderator_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("winner", choose_winner_resort),
            CallbackQueryHandler(callback),
        ],
        states={
            WINNER_RESORT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_winner)
            ],
            WINNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, send_congratulations)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    start_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            RESORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_resort)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(moderator_conv_handler)
    app.add_handler(start_conv_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
