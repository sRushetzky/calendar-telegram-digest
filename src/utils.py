
# ----------------------------------------------------------
# This module handles lightweight local state persistence and hashing.
# The state file (JSON) stores metadata such as last sent message hashes
# and timestamps to prevent duplicate or redundant updates.
# ----------------------------------------------------------

from __future__ import annotations
import json, hashlib
from pathlib import Path
from typing import Any, Dict
from .config import STATE_FILE

def load_state() -> Dict[str, Any]:
    """
    Load the state dictionary from STATE_FILE.
    Returns an empty dict if the file does not exist or cannot be read.
    """
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        # If file is corrupt or unreadable, start fresh
        return {}

def save_state(state: Dict[str, Any]) -> None:
    """
    Save the current state dictionary to STATE_FILE in JSON format.
    Uses UTF-8 encoding and pretty formatting for readability.
    """
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def digest_hash(text: str) -> str:
    """
    Compute a SHA-256 hash for the given text.
    Used to detect whether message content has changed.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
