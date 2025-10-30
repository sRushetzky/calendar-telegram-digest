# src/scheduler.py
from __future__ import annotations
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from .config import TZ, POLL_MINUTES, UPDATE_WINDOW_START, UPDATE_WINDOW_END
from .google_client import (
    resolve_included_calendar_ids,
    iso_range_for_day,
    iso_range_for_week,
    merge_events_from_calendars,
)
from .formatter import format_daily, format_weekly
from .telegram_client import send_message
from .utils import load_state, save_state, digest_hash

tz = pytz.timezone(TZ)

def _is_sunday(dt: datetime) -> bool:
    
    return dt.weekday() == 6

def _today_local() -> datetime:
    return datetime.now(tz)

def send_daily_digest():
    state = load_state()
    cal_ids = resolve_included_calendar_ids()
    today = _today_local()
    tmin, tmax = iso_range_for_day(today)
    events = merge_events_from_calendars(cal_ids, tmin, tmax)
    text = format_daily(today, events)

   
    today_key = today.strftime("%Y-%m-%d")
    last_daily_date = state.get("last_daily_sent_date")
    if last_daily_date == today_key and state.get("last_daily_hash") == digest_hash(text):
        return

    if send_message(text):
        state["last_daily_sent_date"] = today_key
        state["last_daily_hash"] = digest_hash(text)
        save_state(state)

def send_weekly_digest_if_sunday():
    state = load_state()
    now = _today_local()
    if not _is_sunday(now):
        return
    
    wk_key = now.strftime("%Y-W%U")
    if state.get("last_weekly_sent_key") == wk_key:
        return

    
    # כאן נחשב "ראשון" רטרוספקטיבי:
    days_back_to_sunday = (now.weekday() - 6) % 7
    sunday = (now - timedelta(days=days_back_to_sunday)).replace(hour=0, minute=0, second=0, microsecond=0)
    tmin_week, tmax_week = iso_range_for_week(sunday)

    cal_ids = resolve_included_calendar_ids()
    
    days_events = []
    for i in range(7):
        day = sunday + timedelta(days=i)
        dmin, dmax = iso_range_for_day(day)
        evs = merge_events_from_calendars(cal_ids, dmin, dmax)
        days_events.append(evs)

    text = format_weekly(sunday, days_events)
    if send_message(text):
        state["last_weekly_sent_key"] = wk_key
        save_state(state)

def poll_and_send_updates_if_changed():
    
    state = load_state()
    now = _today_local()
    if not (UPDATE_WINDOW_START <= now.hour < UPDATE_WINDOW_END):
        return

    cal_ids = resolve_included_calendar_ids()
    tmin, tmax = iso_range_for_day(now)
    events = merge_events_from_calendars(cal_ids, tmin, tmax)

    from .formatter import format_daily
    text = format_daily(now, events)
    h = digest_hash(text)

    # if equal to last sent hash, no change
    last_hash = state.get("last_daily_hash") or state.get("last_update_hash")
    if last_hash == h:
        return

    # Debounce: if we sent an update recently, wait a bit
    last_update_ts = state.get("last_update_sent_at")
    if last_update_ts:
        try:
            last_dt = datetime.fromisoformat(last_update_ts)
            # wait at least 2 minutes between updates
            if (now - last_dt).total_seconds() < 120:
                return
        except Exception:
            pass

    if send_message("🔄 עדכון בלוח היום\n\n" + text):
        state["last_update_hash"] = h
        state["last_update_sent_at"] = now.isoformat()
        
        if state.get("last_daily_sent_date") != now.strftime("%Y-%m-%d"):
            state["last_daily_hash"] = h
        save_state(state)

def build_scheduler() -> BackgroundScheduler:
    sched = BackgroundScheduler(timezone=TZ)

    # daily at 08:00
    sched.add_job(send_daily_digest, "cron", hour=8, minute=0)

    # in addition, weekly on Sundays at 08:00
    sched.add_job(send_weekly_digest_if_sunday, "cron", day_of_week="sun", hour=8, minute=0)

    # Polling for changes every POLL_MINUTES
    sched.add_job(poll_and_send_updates_if_changed, "interval", minutes=POLL_MINUTES)

    return sched
