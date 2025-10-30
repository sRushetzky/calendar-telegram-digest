
# ----------------------------------------------------------
# This file defines global configuration values and paths
# used across the project. It loads environment variables,
# sets up directory paths, timezone, and constants related
# to Google OAuth, calendars, and scheduler behavior.
# ----------------------------------------------------------

from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Root project directory
ROOT = Path(__file__).resolve().parents[1]

# Load environment variables from .env file
load_dotenv(ROOT / ".env")

# Telegram bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

# Default timezone (can be overridden in .env)
TZ = os.getenv("TZ", "Asia/Jerusalem")

# ----------------------------------------------------------
# OAuth and local data paths
# ----------------------------------------------------------
CREDENTIALS_DIR = ROOT / "credentials"   # Directory for Google OAuth credentials
DATA_DIR = ROOT / "data"                 # Directory for storing runtime data

GOOGLE_CLIENT_SECRET = CREDENTIALS_DIR / "client_secret.json"   # OAuth client secret file
GOOGLE_TOKEN = CREDENTIALS_DIR / "token.json"                   # OAuth access/refresh token
STATE_FILE = DATA_DIR / "state.json"                            # Local file storing previous state

# ----------------------------------------------------------
# Calendar settings
# ----------------------------------------------------------
# Calendar names to include when fetching events.
# 'PRIMARY' represents the user's main calendar.
INCLUDE_CALENDAR_NAMES = [
    "PRIMARY",                # Main calendar
    "Holidays in Israel",     # Israeli holidays (English)
    "Jewish Holidays",        # Jewish holidays (English)
    "חגים בישראל",            # Israeli holidays (Hebrew)
    "חגים יהודיים",           # Jewish holidays (Hebrew)
]

# ----------------------------------------------------------
# Scheduler and polling configuration
# ----------------------------------------------------------
UPDATE_WINDOW_START = 0   # Start hour for update notifications (00:00)
UPDATE_WINDOW_END = 24    # End hour for update notifications (24:00)

POLL_MINUTES = 2          # Interval in minutes between update checks
