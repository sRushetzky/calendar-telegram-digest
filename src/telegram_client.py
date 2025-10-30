# src/telegram_client.py
from __future__ import annotations
import requests
from .config import BOT_TOKEN, CHAT_ID

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(text: str) -> bool:
    try:
        r = requests.post(f"{API_BASE}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",   
            "disable_web_page_preview": True
        }, timeout=15)
        return r.status_code == 200
    except Exception:
        return False
