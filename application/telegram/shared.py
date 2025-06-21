from typing import Callable
from telegram import Update
from telegram.ext import CallbackContext, JobQueue

from application.utils import consts


async def printer(update: Update, context: CallbackContext, text: str) -> None:
    if text.strip() == "":
        text = "💥 CANNOT REPLY WITH EMPTY TEXT"
    print(f"Action result: \n{text}")
    if update.effective_message:
        try:
            await update.effective_message.reply_text(text=text)
            return
        except Exception as e:
            print(f"💥 Reply [update.effective_message.reply_text]: {e}")
            pass
    if update.message:  # that also works
        try:
            await update.message.reply_text(
                text=text
                # , parse_mode="MarkdownV2"
            )
            return
        except Exception as e:
            print(f"💥 Reply [update.message.reply_text]: {e}")
            pass
    # await update.callback_query.answer(
    #     text
    # )  # sometimes fails with telegram.error.BadRequest: Message_too_long
    print(f"Failed to print. Arguments: \n{update} \n\n{context} \n\ntext: {text}")
    try:
        await update.callback_query.message.reply_text(text)
        return
    except Exception as e:
        print(f"💥 Reply [update.callback_query.message]: {e}")


def get_user_id(update: Update, context: CallbackContext) -> str:
    if getattr(update, "effective_user", None) and getattr(
        update.effective_user, "id", None
    ):
        return update.effective_user.id
    elif getattr(context, "_user_id_and_data", None) and context._user_id_and_data[0]:
        return context._user_id_and_data[0]
    else:
        raise Exception("No user_id found")


def initiate_repeating_scheduler(
    job_queue: JobQueue, user_id: str, func: Callable, hours_interval: int = 6
):
    run_every_x_hours = hours_interval * consts.seconds_in_hour
    job_queue.run_repeating(
        func,
        interval=run_every_x_hours,
        first=1,
        data=user_id,
        name=str(user_id),
    )
