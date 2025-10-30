from __future__ import annotations
from datetime import datetime, timedelta
import pytz
from src.google_client import resolve_included_calendar_ids, iso_range_for_day
from src.formatter import format_weekly
from src.telegram_client import send_message
from src.config import TZ

tz = pytz.timezone(TZ)
now = datetime.now(tz)

# מחשבים את יום ראשון הקרוב/נוכחי
days_back_to_sunday = (now.weekday() - 6) % 7
sunday = (now - timedelta(days=days_back_to_sunday)).replace(hour=0, minute=0, second=0, microsecond=0)

cids = resolve_included_calendar_ids()

days_events = []
for i in range(7):
    d = sunday + timedelta(days=i)
    dmin, dmax = iso_range_for_day(d)
    from src.google_client import merge_events_from_calendars
    events = merge_events_from_calendars(cids, dmin, dmax)
    days_events.append(events)

text = format_weekly(sunday, days_events)
ok = send_message(text)
print("sent:", ok)
