
# ----------------------------------------------------------
# This is the main entry point of the application.
# It starts the scheduler (responsible for daily, weekly,
# and real-time calendar update checks) and runs a lightweight
# HTTP server in the background to keep the Render service alive.
# ----------------------------------------------------------

from __future__ import annotations
import time
from threading import Thread

from .scheduler import build_scheduler
from .web import run as run_web


def main():
    """Initialize and run both the scheduler and web server."""
    
    # Start the scheduler (handles daily/weekly digests and polling)
    sched = build_scheduler()
    sched.start()

    # Run the lightweight HTTP server in a background thread
    # Render requires an open port to keep the service active
    t = Thread(target=run_web, daemon=True)
    t.start()

    # Keep the main process running indefinitely
    try:
        while True:
            time.sleep(3600)  # Sleep one hour per loop iteration
    except KeyboardInterrupt:
        # Graceful shutdown on manual interruption
        sched.shutdown()


if __name__ == "__main__":
    main()
