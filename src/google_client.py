
# ----------------------------------------------------------
# This module handles all interactions with the Google Calendar API.
# It manages authentication (OAuth2), retrieves calendar lists,
# fetches events within date ranges, merges events from multiple
# calendars, and localizes date/time ranges for daily and weekly queries.
# Works both locally (with credentials folder) and in the cloud (Render)
# where credentials are stored as Secret Files in /etc/secrets/.
# ----------------------------------------------------------

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
# Determine where the credential files are located.
# In Render, Secret Files are mounted under /etc/secrets/.
# Locally, they are stored under the credentials/ directory.
# ------------------------------------------------------------
RENDER_CLIENT = Path("/etc/secrets/client_secret.json")
RENDER_TOKEN  = Path("/etc/secrets/token.json")

LOCAL_CLIENT  = Path("credentials/client_secret.json")
LOCAL_TOKEN   = Path("credentials/token.json")

# Choose file paths depending on where the code runs
GOOGLE_CLIENT_SECRET = RENDER_CLIENT if RENDER_CLIENT.exists() else LOCAL_CLIENT
GOOGLE_TOKEN         = RENDER_TOKEN  if RENDER_TOKEN.exists()  else LOCAL_TOKEN

# Google API access scope (read-only for calendar)
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _safe_write_token(creds: Credentials) -> None:
    """
    Attempt to safely save the token.json file only if the directory is writable.
    In Render, /etc/secrets/ is usually read-only, so we skip writing errors silently.
    """
    try:
        parent = GOOGLE_TOKEN.parent if GOOGLE_TOKEN.parent else Path(".")
        if parent.exists() and os.access(parent, os.W_OK):
            with open(GOOGLE_TOKEN, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
    except Exception:
        # Not critical — ignore any error when saving token
        pass


def _get_creds() -> Credentials:
    """
    Obtain valid Google OAuth credentials.
    - Uses existing token.json if available.
    - Refreshes expired tokens automatically.
    - Performs interactive authentication if needed (only locally).
    """
    creds = None
    if GOOGLE_TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(GOOGLE_TOKEN), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Transparent refresh of expired token
            creds.refresh(Request())
            _safe_write_token(creds)
        else:
            # Interactive login (local only; in Render token is uploaded manually)
            flow = InstalledAppFlow.from_client_secrets_file(str(GOOGLE_CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
            _safe_write_token(creds)

    return creds


def get_service():
    """Create and return a Google Calendar API service object."""
    creds = _get_creds()
    return build("calendar", "v3", credentials=creds)


def list_calendars() -> List[Dict[str, Any]]:
    """Fetch a paginated list of all calendars accessible by the user."""
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
    Resolve which calendars should be included in the scan based on
    INCLUDE_CALENDAR_NAMES (case-insensitive partial matching).
    'PRIMARY' is identified by primary=True in the API.
    """
    cals = list_calendars()
    ids = set()

    # Add primary calendar if requested
    if any(name.lower() == "primary" for name in INCLUDE_CALENDAR_NAMES):
        for c in cals:
            if c.get("primary"):
                ids.add(c["id"])
                break

    # Match additional calendars by name (case-insensitive, substring)
    wanted = [n.lower() for n in INCLUDE_CALENDAR_NAMES if n.lower() != "primary"]
    for c in cals:
        name = (c.get("summary") or "").lower()
        if any(w in name for w in wanted):
            ids.add(c["id"])

    return list(ids)


def iso_range_for_day(day: datetime) -> Tuple[str, str]:
    """Return ISO time range (start/end) for a specific day in the local timezone."""
    tz = pytz.timezone(TZ)
    start = tz.localize(datetime(day.year, day.month, day.day, 0, 0, 0))
    end = start + timedelta(days=1)
    return start.isoformat(), end.isoformat()


def iso_range_for_week(start_sunday: datetime) -> Tuple[str, str]:
    """Return ISO time range (start/end) for a week starting on a given Sunday."""
    tz = pytz.timezone(TZ)
    start = tz.localize(datetime(start_sunday.year, start_sunday.month, start_sunday.day, 0, 0, 0))
    end = start + timedelta(days=7)
    return start.isoformat(), end.isoformat()


def fetch_events_for_range(calendar_id: str, time_min_iso: str, time_max_iso: str) -> List[Dict[str, Any]]:
    """
    Fetch all events from a given calendar ID within a specific date range.
    Handles pagination and returns a flat list of event dictionaries.
    """
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
    """
    Combine events from multiple calendars into a single chronologically sorted list.
    Each calendar is fetched independently and merged by event start time.
    """
    all_events: List[Dict[str, Any]] = []
    for cid in calendar_ids:
        all_events.extend(fetch_events_for_range(cid, time_min_iso, time_max_iso))

    # Sort all events globally by start time
    def start_key(ev: Dict[str, Any]):
        s = ev.get("start", {})
        if "date" in s:           # all-day events
            return (s["date"], "00:00")
        dt = s.get("dateTime") or ""
        return (dt, "")

    all_events.sort(key=start_key)
    return all_events
