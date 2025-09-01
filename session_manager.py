import json
import streamlit as st

SESSION_KEY = "chat_history"

def save_session(session_data=None):
    """
    Save session chat history into st.session_state.
    Optionally accepts a custom list to save.
    """
    if session_data is None:
        session_data = st.session_state.get(SESSION_KEY, [])
    st.session_state[SESSION_KEY] = session_data

def load_session():
    """
    Load session chat history from st.session_state.
    Returns empty list if not set.
    """
    return st.session_state.get(SESSION_KEY, [])

def export_session():
    """
    Export session history as downloadable JSON string.
    """
    session_data = st.session_state.get(SESSION_KEY, [])
    return json.dumps(session_data, indent=4)

def import_session(uploaded_file):
    """
    Import session history from an uploaded JSON file.
    """
    try:
        content = uploaded_file.read().decode("utf-8")
        st.session_state[SESSION_KEY] = json.loads(content)
        return True
    except Exception as e:
        st.error(f"Error importing session: {e}")
        return False
