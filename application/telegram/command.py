from telegram import Update
from telegram.ext import CallbackContext, ContextTypes, JobQueue

from application.handlers import llm_handlers, g_calendar, counter
from application.handlers import range_handler
from application.telegram.shared import (
    printer,
    get_user_id,
    initiate_repeating_scheduler,
)


async def transcribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.voice.file_id)
    path = f"voice_{update.effective_user.id}.ogg"
    await file.download_to_drive(path)

    await printer(update, context, "Voice received. Processing...")

    transcription = llm_handlers.transcribe(path)
    await printer(update, context, f"🗣️: {transcription}")


async def ask_llm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    result = llm_handlers.ask(query)
    await printer(update, context, f"{result}")


async def check_range(update: Update, context: CallbackContext):
    text = await range_handler.check_range_appointments()
    await printer(update, context, text)


def turn_on_range_monitor(job_queue: JobQueue, user_id: str, hours_interval: int = 6):
    async def check_range_appointments_worker(context: CallbackContext):
        user_id = context.job.data  # we store user_id in job context
        msg = await range_handler.check_range_appointments()
        print(msg)
        await context.application.bot.send_message(chat_id=user_id, text=msg)

    initiate_repeating_scheduler(
        job_queue, user_id, check_range_appointments_worker, hours_interval
    )


async def toggle_range_monitor(update: Update, context: CallbackContext):
    user_id = get_user_id(update, context)
    new_state = not range_handler.get_range_monitor_states(user_id)
    range_handler.monitor_states[user_id] = new_state
    if new_state:  # Turn it on
        turn_on_range_monitor(context.job_queue, user_id)
        text = "Appointments Monitor turned ON"
    else:  # Turn it off
        #  TODO move to range
        for job in context.job_queue.get_jobs_by_name(str(user_id)):
            job.schedule_removal()
        text = "Appointments Monitor turned OFF"
    await printer(update, context, text)


async def tupac(update: Update, context: CallbackContext):
    await printer(update, context, "got my diploma but I never learned shit in school")


async def boxing(update: Update, context: CallbackContext):
    events = g_calendar.get_boxing_data()
    text = events  # Use "\n".join(events) if events is a list
    await printer(update, context, text)


async def smoke(update: Update, context: CallbackContext):
    text = counter.get_time_since(
        2024, 4, 28, 14, 0, "Time since You quit smoking (April 27, 2024 14:00) is"
    )
    await printer(update, context, text)


async def boy(update: Update, context: CallbackContext):
    text = counter.get_time_since(
        2024, 8, 28, 23, 5, "Time since Boy was born (August 28th, 2024 23:05) is"
    )
    await printer(update, context, text)
