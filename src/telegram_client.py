
# ----------------------------------------------------------
# This module provides a simple interface for sending messages
# to a specific Telegram chat via the Telegram Bot API.
# It uses the BOT_TOKEN and CHAT_ID from environment variables
# (loaded via config.py) and wraps requests.post with error handling.
# ----------------------------------------------------------

from __future__ import annotations
import requests
from .config import BOT_TOKEN, CHAT_ID

# Base URL for the Telegram Bot API (unique per bot token)
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(text: str) -> bool:
    """
    Send a text message to the configured Telegram chat.
    Returns True if the request succeeded (HTTP 200), False otherwise.
    """
    try:
        r = requests.post(
            f"{API_BASE}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",       # Enables bold/italic/etc.
                "disable_web_page_preview": True # Avoids large link previews
            },
            timeout=15
        )
        return r.status_code == 200
    except Exception:
        # Any connection or timeout error is silently ignored
        return False
