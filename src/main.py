# src/main.py
from __future__ import annotations
import time
from .scheduler import build_scheduler

def main():
    sched = build_scheduler()
    sched.start()
    print("Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down scheduler...")
        sched.shutdown()

if __name__ == "__main__":
    main()
