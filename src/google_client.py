# src/google_client.py
from __future__ import annotations
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import pytz

from .config import GOOGLE_CLIENT_SECRET, GOOGLE_TOKEN, TZ, INCLUDE_CALENDAR_NAMES

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def _get_creds() -> Credentials:
    creds = None
    if GOOGLE_TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(GOOGLE_TOKEN), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(GOOGLE_CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_TOKEN, "w") as f:
            f.write(creds.to_json())
    return creds

def get_service():
    creds = _get_creds()
    return build("calendar", "v3", credentials=creds)

def list_calendars() -> List[Dict[str, Any]]:
    service = get_service()
    items = []
    page_token = None
    while True:
        resp = service.calendarList().list(pageToken=page_token).execute()
        items.extend(resp.get("items", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return items

def resolve_included_calendar_ids() -> List[str]:
    """
    מחזיר רשימת calendarId שנכללים בלוז, לפי שמות ב-INCLUDE_CALENDAR_NAMES.
    'PRIMARY' מזוהה דרך primary=true.
    """
    cals = list_calendars()
    ids = set()

    # זיהוי PRIMARY
    for c in cals:
        if c.get("primary"):
            if any(name.lower() == "primary" for name in INCLUDE_CALENDAR_NAMES):
                ids.add(c["id"])
            break

    # התאמה לפי שם (case-insensitive, גם contains)
    wanted = [n.lower() for n in INCLUDE_CALENDAR_NAMES if n.lower() != "primary"]
    for c in cals:
        name = (c.get("summary") or "").lower()
        for w in wanted:
            if w in name:
                ids.add(c["id"])
                break

    return list(ids)

def iso_range_for_day(day: datetime) -> (str, str):
    tz = pytz.timezone(TZ)
    start = tz.localize(datetime(day.year, day.month, day.day, 0, 0, 0))
    end = start + timedelta(days=1)
    return start.isoformat(), end.isoformat()

def iso_range_for_week(start_sunday: datetime) -> (str, str):
    tz = pytz.timezone(TZ)
    start = tz.localize(datetime(start_sunday.year, start_sunday.month, start_sunday.day, 0, 0, 0))
    end = start + timedelta(days=7)
    return start.isoformat(), end.isoformat()

def fetch_events_for_range(calendar_id: str, time_min_iso: str, time_max_iso: str) -> List[Dict[str, Any]]:
    service = get_service()
    events: List[Dict[str, Any]] = []
    page_token = None
    while True:
        resp = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min_iso,
            timeMax=time_max_iso,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events.extend(resp.get("items", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return events

def merge_events_from_calendars(calendar_ids: List[str], time_min_iso: str, time_max_iso: str) -> List[Dict[str, Any]]:
    all_events: List[Dict[str, Any]] = []
    for cid in calendar_ids:
        all_events.extend(fetch_events_for_range(cid, time_min_iso, time_max_iso))
    # ממילא events().list הוחזרו מסודרים לכל לוח; נמיין מחדש לפי זמן התחלה כדי לאחד
    def start_key(ev):
        s = ev.get("start", {})
        # all-day
        if "date" in s:
            return (s["date"], "00:00")
        # timed
        dt = s.get("dateTime") or ""
        return (dt, "")
    all_events.sort(key=start_key)
    return all_events
