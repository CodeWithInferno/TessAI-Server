# agents/scheduler_agent/logic.py

import dateparser
from datetime import datetime, timedelta
from agents.scheduler_agent.db import get_events_on_day
from datetime import datetime, timedelta

def format_event(event_row):
    _, title, start_ts, end_ts, location, _ = event_row
    time_str = datetime.fromisoformat(start_ts).strftime("%I:%M %p")
    loc_str = f" at {location}" if location else ""
    return f"- {title} at {time_str}{loc_str}"

def get_agenda_for_day(natural_date = "today"):
    date_obj = dateparser.parse(str(natural_date))  # ✅ always cast to str
    if not date_obj:
        return "❌ I couldn't understand the date."

    date_str = date_obj.strftime("%Y-%m-%d")
    events = get_events_on_day(date_str)

    if not events:
        return f"✅ You're free on {natural_date} ({date_str})!"

    response = f"📅 Here's your agenda for {natural_date}:\n"
    for event in events:
        response += format_event(event) + "\n"
    return response.strip()

def is_time_free(natural_datetime: str):
    check_dt = dateparser.parse(natural_datetime)
    if not check_dt:
        return "❌ I couldn't understand the time."

    date_str = check_dt.strftime("%Y-%m-%d")
    time = check_dt.time()

    events = get_events_on_day(date_str)
    for event in events:
        _, title, start_ts, end_ts, _, _ = event
        start = datetime.fromisoformat(start_ts)
        end = datetime.fromisoformat(end_ts) if end_ts else start + timedelta(hours=1)

        if start.time() <= time <= end.time():
            return f"❌ You're busy then: '{title}' from {start.time()} to {end.time()}."

    return "✅ You're free at that time."
