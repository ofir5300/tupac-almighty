import requests

from application.utils import utils

DEFAULT_USER_ID = utils.load_secret("TELEGRAM_DEFAULT_USER_ID")
monitor_states = {int(DEFAULT_USER_ID): True}  # { user_id: bool }


async def fetch_range_appointments() -> dict:
    url = "https://mitvah-rehovot.co.il/appointments/api/availables/?departmentId=197"
    resp = requests.get(url)
    return resp.json()


async def check_range_appointments() -> str:
    data = await fetch_range_appointments()
    findings = []
    pas = data[
        "possibleAppointments"
    ]  # sometimes [] if empty, other times { ... } if full

    if isinstance(pas, dict):  # It's a dictionary: iterate over date -> [times]
        for date_str, times in pas.items():
            if times:
                findings.append(f"{date_str}: {', '.join(times)}")
    elif isinstance(pas, list):  # It's a list: if empty, there's nothing to report
        pass

    if findings:
        return "Yo, Shooting Range appointments found:\n" + "\n".join(findings)
    else:
        return "No Shooting Range appointments found"


def get_range_monitor_states(user_id: str) -> bool:
    return monitor_states.get(user_id, False)  # TODO.abuse - change
