# src/utils.py
from __future__ import annotations
import json, hashlib
from pathlib import Path
from typing import Any, Dict
from .config import STATE_FILE

def load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_state(state: Dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def digest_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
