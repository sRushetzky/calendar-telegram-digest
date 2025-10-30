from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
TZ = os.getenv("TZ", "Asia/Jerusalem")

# נתיבים לקבצי OAuth/מצב
CREDENTIALS_DIR = ROOT / "credentials"
DATA_DIR = ROOT / "data"
GOOGLE_CLIENT_SECRET = CREDENTIALS_DIR / "client_secret.json"
GOOGLE_TOKEN = CREDENTIALS_DIR / "token.json"
STATE_FILE = DATA_DIR / "state.json"

# שמות לוחות שנכללים בלוז (נשתמש בחיפוש לפי שם – גמיש לשפות)
# חשוב: PRIMARY מייצג את הלוח הראשי שלך.
INCLUDE_CALENDAR_NAMES = [
    "PRIMARY",                # הלוח הראשי
    "Holidays in Israel",     # חגים בישראל
    "Jewish Holidays",        # חגים יהודיים כלליים
    "חגים בישראל",            # גרסה בעברית (אם מופיעה כך)
     "חגים יהודיים",            # גרסה בעברית (אם מופיעה כך)
]

# חלון שעות לעדכונים מיידיים (כדי לא להציף בלילה)
UPDATE_WINDOW_START = 0   # 00:00
UPDATE_WINDOW_END = 24    # 24:00

# כמה דקות בין בדיקות שינוי (polling)
POLL_MINUTES = 2
