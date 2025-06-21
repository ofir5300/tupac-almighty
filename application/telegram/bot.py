import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import CallbackContext

from application.handlers import range_handler
import application.utils.consts as consts
import application.telegram.command as command

logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: CallbackContext):
    logger.error("An error occurred:", exc_info=context.error)
    if update and update.callback_query:
        await update.callback_query.message.reply_text(
            f"⛔️ An error occurred: {str(context.error)}"
        )


async def start(update: Update, context: CallbackContext):
    user_id = command.get_user_id(update, context)
    monitor_status = "On" if range_handler.get_range_monitor_states(user_id) else "Off"

    keyboard = [
        [
            InlineKeyboardButton("Tupac", callback_data=consts.tupac),
            InlineKeyboardButton("Boxing classes", callback_data=consts.boxing),
        ],
        [
            InlineKeyboardButton("Smoke Counter", callback_data=consts.smoke),
            InlineKeyboardButton("Boy Old", callback_data=consts.boy),
        ],
        [
            InlineKeyboardButton(
                f"Range Monitor: {monitor_status}",
                callback_data=consts.toggle_range_monitor,
            ),
            InlineKeyboardButton("Check Range", callback_data=consts.check_range),
        ],
    ]

    message = update.effective_message
    if message:
        await message.reply_text(
            "Choose action:", reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def button(update: Update, context: CallbackContext):
    query: CallbackQuery = update.callback_query
    data = query.data

    if data == consts.check_range:
        await command.check_range(update, context)
    elif data == consts.toggle_range_monitor:
        await command.toggle_range_monitor(update, context)
    elif data == consts.tupac:
        await command.tupac(update, context)
    elif data == consts.boxing:
        await command.boxing(update, context)
    elif data == consts.smoke:
        await command.smoke(update, context)
    elif data == consts.boy:
        await command.boy(update, context)
    else:
        raise Exception("Invalid option selected.")

    logger.info("you clicked %s", data)
    await start(update, context)
