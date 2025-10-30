from __future__ import annotations
from .google_client import get_service, list_calendars

def main():
    svc = get_service()          # יפתח דפדפן להרשאה אם צריך
    cals = list_calendars()      # קריאה ראשונה: מאמתת שהכול עובד
    print(f"Found {len(cals)} calendars. Auth OK ✅")

if __name__ == "__main__":
    main()
