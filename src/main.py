# src/main.py
from __future__ import annotations
import time
from threading import Thread

from .scheduler import build_scheduler
from .web import run as run_web

def main():
    # מפעיל את הסקד׳יולר (שליחה יומית, שבועית, ופול לשינויים)
    sched = build_scheduler()
    sched.start()

    # מפעיל את שרת ה-HTTP הקטן ברקע כדי של-Render יהיה פורט פתוח
    t = Thread(target=run_web, daemon=True)
    t.start()

    # מונע מהתהליך להסתיים
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        sched.shutdown()

if __name__ == "__main__":
    main()
