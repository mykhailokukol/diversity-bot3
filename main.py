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
    WINNER,
    start,
    choose_winner,
    send_congratulations,
    callback,
    cancel,
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
            CommandHandler("winner", choose_winner),
            CallbackQueryHandler(callback),
        ],
        states={
            WINNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, send_congratulations)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(moderator_conv_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
