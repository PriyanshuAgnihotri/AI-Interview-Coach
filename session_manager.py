import json
import os

SESSION_FILE = "session_data.json"

def save_session(session_data):
    """
    Save session chat history to JSON file.
    """
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(session_data, f, indent=4)
    except Exception as e:
        print(f"Error saving session: {e}")

def load_session():
    """
    Load session chat history from JSON file.
    Returns empty list if no file exists.
    """
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return []
    return []
