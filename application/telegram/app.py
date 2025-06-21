import logging
import time

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

import application.utils.consts as consts
from application.telegram import bot, command
from application.utils import utils

time.tzset()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)  # Suppress INFO logs from httpx


def build():
    app = ApplicationBuilder().token(utils.load_secret("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler(consts.check_range, command.check_range))
    app.add_handler(
        CommandHandler(consts.toggle_range_monitor, command.toggle_range_monitor)
    )
    app.add_handler(CommandHandler(consts.tupac, command.tupac))
    app.add_handler(CommandHandler(consts.boxing, command.boxing))
    app.add_handler(CommandHandler(consts.smoke, command.smoke))
    app.add_handler(CommandHandler(consts.boy, command.boy))

    app.add_handler(CallbackQueryHandler(bot.button))

    app.add_handler(MessageHandler(filters.VOICE, command.transcribe))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, command.ask_llm))

    app.add_error_handler(bot.error_handler)

    DEFAULT_USER_ID = utils.load_secret("TELEGRAM_DEFAULT_USER_ID")
    text = "🔫 Tupac is up 🪓"
    logging.info(text)
    command.turn_on_range_monitor(
        app.job_queue, DEFAULT_USER_ID
    )  # on start, turn on by default

    utils.use_asyncio(app.bot.send_message(chat_id=DEFAULT_USER_ID, text=text))
    app.run_polling()
