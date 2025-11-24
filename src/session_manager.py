import os
import json
from datetime import datetime
from typing import List, Dict, Any

SESSION_DIR = "session_data"


def _ensure_session_dir():
    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR, exist_ok=True)


def _session_path(user: str) -> str:
    _ensure_session_dir()
    safe_user = user.replace("@", "_at_").replace(" ", "_")
    return os.path.join(SESSION_DIR, f"{safe_user}.json")


def load_session(user: str) -> List[Dict[str, Any]]:
    """
    Load session events for a user.
    Each event: { "timestamp": str, "type": str, "value": str }
    """
    path = _session_path(user)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_session(user: str, events: List[Dict[str, Any]]) -> None:
    """
    Overwrite session file for a user.
    """
    path = _session_path(user)
    with open(path, "w") as f:
        json.dump(events, f, indent=2)


def add_event(user: str, event_type: str, value: str) -> None:
    """
    Append a new event to the user's session.
    """
    events = load_session(user)
    events.append(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "value": value.strip().lower(),
        }
    )
    save_session(user, events)


def clear_session(user: str) -> None:
    """
    Clear a user's session.
    """
    path = _session_path(user)
    if os.path.exists(path):
        os.remove(path)


def get_recent_events(user: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Return the most recent 'limit' events.
    """
    events = load_session(user)
    return events[-limit:]
