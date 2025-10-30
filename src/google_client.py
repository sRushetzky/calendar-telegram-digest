# src/google_client.py
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from pathlib import Path
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pytz

from .config import TZ, INCLUDE_CALENDAR_NAMES

# ------------------------------------------------------------
# היכן נמצאים קבצי ההרשאה
# Render שומר Secret Files תחת /etc/secrets/ (ללא תיקיות)
# בלוקאל נשארים תחת credentials/
# ------------------------------------------------------------
RENDER_CLIENT = Path("/etc/secrets/client_secret.json")
RENDER_TOKEN  = Path("/etc/secrets/token.json")

LOCAL_CLIENT  = Path("credentials/client_secret.json")
LOCAL_TOKEN   = Path("credentials/token.json")

GOOGLE_CLIENT_SECRET = RENDER_CLIENT if RENDER_CLIENT.exists() else LOCAL_CLIENT
GOOGLE_TOKEN         = RENDER_TOKEN  if RENDER_TOKEN.exists()  else LOCAL_TOKEN

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _safe_write_token(creds: Credentials) -> None:
    """
    מנסה לשמור token.json, רק אם הנתיב ניתן לכתיבה.
    ב-Render בדרך כלל /etc/secrets לא ניתן לכתיבה, אז נדלג בשקט.
    """
    try:
        parent = GOOGLE_TOKEN.parent if GOOGLE_TOKEN.parent else Path(".")
        if parent.exists() and os.access(parent, os.W_OK):
            with open(GOOGLE_TOKEN, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
    except Exception:
        # לא קריטי לריצה – מתעלמים משגיאה בשמירה
        pass


def _get_creds() -> Credentials:
    creds = None
    if GOOGLE_TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(GOOGLE_TOKEN), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # רענון שקוף
            creds.refresh(Request())
            _safe_write_token(creds)
        else:
            # התחברות אינטראקטיבית (רק בלוקאל; בענן נשתמש בטוקן שהועלה כ-Secret File)
            flow = InstalledAppFlow.from_client_secrets_file(str(GOOGLE_CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
            _safe_write_token(creds)

    return creds


def get_service():
    """יוצר אובייקט שירות של Google Calendar."""
    creds = _get_creds()
    return build("calendar", "v3", credentials=creds)


def list_calendars() -> List[Dict[str, Any]]:
    """רשימת כל לוחות השנה של המשתמש (עם דפדוף)."""
    service = get_service()
    items: List[Dict[str, Any]] = []
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
    מחזיר רשימת calendarId שנכללים בלו"ז לפי שמות ב-INCLUDE_CALENDAR_NAMES.
    'PRIMARY' מזוהה דרך primary=true. התאמה לשמות היא case-insensitive וגם contains.
    """
    cals = list_calendars()
    ids = set()

    # PRIMARY
    if any(name.lower() == "primary" for name in INCLUDE_CALENDAR_NAMES):
        for c in cals:
            if c.get("primary"):
                ids.add(c["id"])
                break

    # התאמה לפי שם
    wanted = [n.lower() for n in INCLUDE_CALENDAR_NAMES if n.lower() != "primary"]
    for c in cals:
        name = (c.get("summary") or "").lower()
        if any(w in name for w in wanted):
            ids.add(c["id"])

    return list(ids)


def iso_range_for_day(day: datetime) -> Tuple[str, str]:
    tz = pytz.timezone(TZ)
    start = tz.localize(datetime(day.year, day.month, day.day, 0, 0, 0))
    end = start + timedelta(days=1)
    return start.isoformat(), end.isoformat()


def iso_range_for_week(start_sunday: datetime) -> Tuple[str, str]:
    tz = pytz.timezone(TZ)
    start = tz.localize(datetime(start_sunday.year, start_sunday.month, start_sunday.day, 0, 0, 0))
    end = start + timedelta(days=7)
    return start.isoformat(), end.isoformat()


def fetch_events_for_range(calendar_id: str, time_min_iso: str, time_max_iso: str) -> List[Dict[str, Any]]:
    service = get_service()
    events: List[Dict[str, Any]] = []
    page_token = None
    while True:
        resp = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min_iso,
                timeMax=time_max_iso,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events.extend(resp.get("items", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return events


def merge_events_from_calendars(calendar_ids: List[str], time_min_iso: str, time_max_iso: str) -> List[Dict[str, Any]]:
    all_events: List[Dict[str, Any]] = []
    for cid in calendar_ids:
        all_events.extend(fetch_events_for_range(cid, time_min_iso, time_max_iso))

    # מיון גלובלי לפי זמן התחלה
    def start_key(ev: Dict[str, Any]):
        s = ev.get("start", {})
        if "date" in s:           # all-day
            return (s["date"], "00:00")
        dt = s.get("dateTime") or ""
        return (dt, "")

    all_events.sort(key=start_key)
    return all_events
