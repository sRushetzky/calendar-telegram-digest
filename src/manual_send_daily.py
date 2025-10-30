from __future__ import annotations
from datetime import datetime
import pytz
from src.google_client import resolve_included_calendar_ids, iso_range_for_day, merge_events_from_calendars
from src.formatter import format_daily
from src.telegram_client import send_message
from src.config import TZ

tz = pytz.timezone(TZ)
today = datetime.now(tz)
cids = resolve_included_calendar_ids()
tmin, tmax = iso_range_for_day(today)
events = merge_events_from_calendars(cids, tmin, tmax)
text = format_daily(today, events)
ok = send_message(text)
print("sent:", ok)
