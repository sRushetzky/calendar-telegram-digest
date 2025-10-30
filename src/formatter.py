
# ----------------------------------------------------------
# This module handles all text formatting for Telegram messages.
# It builds daily and weekly schedules in Markdown, formats event
# details (time, title, location), adds emojis contextually based
# on event type, and provides helper functions for localization
# and date/time handling.
# ----------------------------------------------------------

from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import pytz
from .config import TZ

# ---------- Markdown helpers ----------
def escape_md(text: Optional[str]) -> str:
    """Escape Markdown special characters to avoid formatting issues."""
    if not text:
        return ""
    return re.sub(r"([\\_*\[\]\(\)`])", r"\\\1", str(text))

def bold(s: str) -> str:
    """Return text in bold Markdown format."""
    return f"*{s}*"


# ---------- i18n / time ----------
def _fmt_time(dt_str: str) -> str:
    """Convert ISO datetime string to localized HH:MM format."""
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    tz = pytz.timezone(TZ)
    local = dt.astimezone(tz)
    return local.strftime("%H:%M")

def _weekday_he(dt: datetime) -> str:
    """Return the Hebrew short name for a weekday (Monday=0 ... Sunday=6)."""
    days = ["ב׳", "ג׳", "ד׳", "ה׳", "ו׳", "ש׳", "א׳"]  # ב=Mon, ... א=Sun
    return days[dt.weekday()]


# ---------- domain heuristics (emojis & tags) ----------
# Lists of keywords used to detect event types for adding emojis
BIRTHDAY_TRIGGERS = ["birthday", "יום הולדת", "יומולדת", "מזל טוב", "b-day", "bday", "🎂"]
MACCABI_TRIGGERS   = ["מכבי תל אביב", "מכבי ת\"א", "מכבי ת״א", "maccabi tel aviv", "maccabi ta", "maccabi"]
BLOOMFIELD_TRIGGERS = ["בלומפילד", "bloomfield"]

LECTURE_TRIGGERS = ["lecture", "שיעור", "הרצאה", "קורס"]
MEETING_TRIGGERS = ["meeting", "ישיבה", "פגישה", "sync", "standup", "ישיבת"]
EXAM_TRIGGERS    = ["exam", "מבחן", "בוחן", "test"]
TENNIS_TRIGGERS  = ["טניס", "tennis"]
HAIRCUT_TRIGGERS = ["תור לגיא"]  

# Lecture-related locations that should always show a 🎓 emoji
LECTURE_LOCATION_TRIGGERS = [
    "zoom",
    "Zoom"
    "מכון טכנולוגי חולון",
    "רח' יעקב פיכמן 18, חולון, ישראל",
    "רח\" יעקב פיכמן 18, חולון, ישראל",
    "רח יעקב פיכמן 18, חולון, ישראל",
]

# Calendar names used to detect holidays
HOLIDAY_CAL_NAMES = [
    "holidays in israel",
    "חגים בישראל",
    "jewish holidays",
    "חגים יהודיים",
]

def is_birthday(summary: str) -> bool:
    """Check if event is a birthday."""
    s = (summary or "").lower()
    return any(t in s for t in BIRTHDAY_TRIGGERS)

def is_maccabi(summary: str) -> bool:
    """Check if event is a Maccabi Tel Aviv game."""
    s = (summary or "").lower()
    return any(t in s for t in MACCABI_TRIGGERS)

def is_bloomfield(location: Optional[str]) -> bool:
    """Check if event takes place at Bloomfield Stadium."""
    if not location:
        return False
    s = location.lower()
    return any(t in s for t in BLOOMFIELD_TRIGGERS)

def is_tennis(summary: str) -> bool:
    """Check if event is related to tennis."""
    s = (summary or "").lower()
    return any(t in s for t in TENNIS_TRIGGERS)

def is_haircut(summary: str) -> bool:
    """Check if event is a haircut appointment."""
    s = (summary or "").lower()
    return any(t in s for t in HAIRCUT_TRIGGERS)

def is_lecture_location(location: Optional[str]) -> bool:
    """Check if event location is recognized as a lecture location."""
    if not location:
        return False
    s = location.lower()
    return any(t in s for t in [x.lower() for x in LECTURE_LOCATION_TRIGGERS])

def is_holiday_event(ev: Dict) -> bool:
    """Detect if an event is a holiday based on its calendar or title."""
    for key in ("organizer", "creator"):
        name = (ev.get(key, {}) or {}).get("displayName") or (ev.get(key, {}) or {}).get("email") or ""
        if any(cal.lower() in str(name).lower() for cal in HOLIDAY_CAL_NAMES):
            return True
   
    summary = (ev.get("summary") or "").lower()
    generic_holiday_terms = [
        "holiday", "eve", "ערב חג", "חג ", "ראש השנה", "יום כיפור", "סוכות",
        "פסח", "שמחת תורה", "פורים", "חנוכה", "ט״ו בשבט", "טו בשבט", "שבועות",
        "ל\"ג בעומר", "לג בעומר"
    ]
    if any(t in summary for t in generic_holiday_terms):
        return True
    return False

def extra_emoji(summary: str, location: Optional[str], ev: Dict) -> str:
    """Add context-specific emojis to the event based on keywords or location."""
    s = (summary or "").lower()
    out = ""

    if is_holiday_event(ev):
        out += " ✡️"
    if is_birthday(summary):
        out += " 🎉"
    if is_maccabi(summary):
        out += " ⚽"
        out += " 🏠" if is_bloomfield(location) else " ✈️"
    if is_tennis(summary):
        out += " 🎾"
    if is_haircut(summary):
        out += " ✂️"
    if is_lecture_location(location) or any(t in s for t in LECTURE_TRIGGERS):
        out += " 🎓"
    if any(t in s for t in EXAM_TRIGGERS):
        out += " 🧪"
    if any(t in s for t in MEETING_TRIGGERS):
        out += " 💼"

    return out


# ---------- location formatting ----------
def first_location_segment(location: str) -> str:
    """
    Return only the part of the address before the first comma.
    Example:
    "מרכז הטניס אשקלון, שד' אברהם עופר, אשקלון, ישראל" -> "מרכז הטניס אשקלון"
    "Zoom Meeting, https://..." -> "Zoom Meeting"
    """
    seg = location.split(",", 1)[0].strip()
    return seg or location.strip()


# ---------- line builders ----------
def format_event_line(ev: Dict) -> str:
    """Format a single event line with time, title, emojis, and location."""
    start = ev.get("start", {})
    end = ev.get("end", {})
    summary = ev.get("summary", "(ללא כותרת)")
    location = ev.get("location")

    # Format time (all-day or specific hours)
    if "date" in start:
        time_part = bold("כל היום")
    else:
        t1 = _fmt_time(start.get("dateTime"))
        t2 = _fmt_time(end.get("dateTime"))
        time_part = bold(f"{t1} – {t2}")

    # Add emojis based on context
    add = extra_emoji(summary, location, ev)
    title = f"{escape_md(summary)}{add}"

    lines = [f"• {time_part}  |  {title}"]

    # Include short location (before first comma)
    if location:
        loc_short = first_location_segment(location)
        lines.append(f"  📍 {escape_md(loc_short)}")

    return "\n".join(lines)


# ---------- public API ----------
def format_daily(date_obj: datetime, events: List[Dict]) -> str:
    """Format the daily schedule message for a given date."""
    date_str = date_obj.strftime("%d/%m/%Y")
    header = bold(f"📅 לוח היום — {_weekday_he(date_obj)}, {date_str}")

    if not events:
        return f"{header}\n\nאין אירועים היום ✅😎"

    out_lines: List[str] = [header, ""]
    for idx, ev in enumerate(events):
        out_lines.append(format_event_line(ev))
        # Add two blank lines between events for readability
        out_lines.append("")
        out_lines.append("")

    return "\n".join(out_lines).rstrip()

def format_weekly(start_sunday: datetime, days_events: List[List[Dict]]) -> str:
    """Format the weekly schedule message starting from Sunday."""
    end = start_sunday + timedelta(days=6)
    title = bold(f"🗓️ לוח שבועי — {start_sunday.strftime('%d/%m')}–{end.strftime('%d/%m')}")

    parts: List[str] = [title]
    for i in range(7):
        day = start_sunday + timedelta(days=i)
        date_str = day.strftime("%d/%m/%Y")
        parts.append(f"\n{bold(f'{_weekday_he(day)} {date_str}')}")

        evs = days_events[i]
        if not evs:
            parts.append("אין אירועים.")
            continue

        for ev in evs:
            parts.append(format_event_line(ev))
            # Add two blank lines between events for readability
            parts.append("")
            parts.append("")

    return "\n".join(parts).rstrip()
