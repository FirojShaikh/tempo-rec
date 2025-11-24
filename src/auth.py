import json
import streamlit as st

USERS_FILE = "config/users.json"


def load_users():
    """Load user credentials from users.json"""
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def authenticate(username: str, password: str):
    """Validate username + password. Returns role or None."""
    users = load_users()
    if username in users and users[username]["password"] == password:
        return users[username]["role"]
    return None


def set_logged_in_user(username: str, role: str):
    """Store user state in session."""
    st.session_state["is_authenticated"] = True
    st.session_state["username"] = username
    st.session_state["role"] = role


def logout():
    """Clear authentication state."""
    st.session_state["is_authenticated"] = False
    st.session_state["username"] = "guest"
    st.session_state["role"] = "guest"


def get_current_user():
    """Return (username, role)."""
    if st.session_state.get("is_authenticated"):
        return st.session_state.get("username"), st.session_state.get("role")
    return None, None
