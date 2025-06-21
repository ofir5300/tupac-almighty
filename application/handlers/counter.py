import pytz
from datetime import datetime


def pretty_date_delta(start, end, message):
    delta = end - start
    delta_seconds = int(delta.total_seconds())
    days, remainder = divmod(delta_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    months, days = divmod(days, 30)

    parts = []
    if months > 0:
        parts.append(f"{months} months")
    if days > 0:
        parts.append(f"{days} days")
    if hours > 0:
        parts.append(f"{hours} hours")
    if minutes > 0:
        parts.append(f"{minutes} minutes")
    if seconds > 0:
        parts.append(f"{seconds} seconds")

    return f"{message}:\n{', '.join(parts)}. Which are total of {delta.days} days"


def get_time_since(year, month, day, hour, minute, message):
    israel_tz = pytz.timezone("Asia/Jerusalem")
    start_time = israel_tz.localize(datetime(year, month, day - 1, hour, minute, 0))
    now_time = datetime.now(israel_tz)
    return pretty_date_delta(start_time, now_time, message)
