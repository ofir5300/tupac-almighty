import datetime
import google.oauth2.credentials
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from application.utils.utils import load_secret


def get_boxing_data():
    recent_20th = get_recent_20th()
    events = get_events(recent_20th)
    print(events)
    return build_message(events, 4)


def get_events(since):
    # Replace with the service account email and path to the private key file
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    SERVICE_ACCOUNT_FILE = "./config/secrets/tupac-google-service-account.json"
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # Replace with the ID of the calendar you want to retrieve events from
    calendar_id = load_secret("GOOGLE_CALENDAR_ID")
    try:
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        recent_20th = get_recent_20th()
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=since,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        events = []

    event_strings = []
    for event in events:
        date = event["start"].get("dateTime", event["start"].get("date"))
        formatted_date_str = datetime.datetime.strptime(date[:10], "%Y-%m-%d").strftime(
            "%d/%m"
        )
        # formatted_date_str = datetime.datetime.strptime(
        #     date[:-6], "%Y-%m-%dT%H:%M:%S.%f"
        # ).strftime("%d/%m %H:%M")
        event_string = f'{formatted_date_str} - {event["summary"]}'
        print(event_string)
        event_strings.append(event_string)

    return event_strings


def get_recent_20th():
    today = datetime.date.today()

    if today.day > 20:
        recent_20th = datetime.date(today.year, today.month, 20)
    else:
        last_day_prev_month = datetime.date(
            today.year, today.month, 1
        ) - datetime.timedelta(days=1)
        recent_20th = datetime.date(
            last_day_prev_month.year, last_day_prev_month.month, 20
        )

    return (
        datetime.datetime(
            recent_20th.year, recent_20th.month, recent_20th.day
        ).strftime("%Y-%m-%dT%H:%M:%S.%f")
        + "Z"
    )


def build_message(events, total):
    number_of_events = len(events)
    remaining = total - number_of_events
    remaining_str = str(remaining) if remaining != 20 else "no"
    event_dates_str = "\n".join(events)
    return f"You have {remaining_str} open slots to use until the next 20th.\nYou already used {number_of_events}/{total} slots since the last subscription:\n {event_dates_str}."
