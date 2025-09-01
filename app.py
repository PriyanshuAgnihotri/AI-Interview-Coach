import os
import json
import streamlit as st
from prompts import SYSTEM_PROMPT_TEMPLATE
import openai

# NEW IMPORTS
from voice_input import transcribe_audio
from voice_output import text_to_speech_elevenlabs

# -----------------------------
# Session Manager (integrated)
# -----------------------------
SESSION_KEY = "chat"

def save_session(session_data=None):
    if session_data is None:
        session_data = st.session_state.get(SESSION_KEY, [])
    st.session_state[SESSION_KEY] = session_data

def load_session():
    return st.session_state.get(SESSION_KEY, [])

def export_session():
    session_data = st.session_state.get(SESSION_KEY, [])
    return json.dumps(session_data, indent=4)

def import_session(uploaded_file):
    try:
        content = uploaded_file.read().decode("utf-8")
        st.session_state[SESSION_KEY] = json.loads(content)
        return True
    except Exception as e:
        st.error(f"Error importing session: {e}")
        return False

# -----------------------------
# API Key Setup
# -----------------------------
def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass
    return api_key


# Streamlit UI
st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="wide")
st.title("🎯 AI Interview Coach — Live Demo (Text + Voice)")

api_key = get_api_key()
if api_key:
    openai.api_key = api_key
else:
    st.warning("No OPENAI_API_KEY found. Set it to call the OpenAI API. The app will show MOCK responses without a key.")

# Initialize chat
if SESSION_KEY not in st.session_state:
    st.session_state[SESSION_KEY] = load_session() or [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(role="SDE", type="Behavioral")}
    ]

role = st.selectbox("Role", ["SDE", "Data Analyst", "ML Engineer", "Product Manager"], index=0, key="role")
interview_type = st.selectbox("Interview Type", ["Behavioral", "Technical", "HR"], index=0, key="interview_type")

# Show the current question clearly (last assistant message if exists)
last_msg = st.session_state[SESSION_KEY][-1]["content"] if st.session_state[SESSION_KEY] and st.session_state[SESSION_KEY][-1]["role"] == "assistant" else None
if last_msg:
    st.markdown(f"### Q: {last_msg}")

# Answer input
user_input = st.text_area("Your answer (or use voice input)", height=200)

# Voice input support
audio = st.file_uploader("🎤 Upload your voice answer (mp3/wav)", type=["mp3", "wav"])
if audio:
    text_response = transcribe_audio(audio)
    st.write("You said:", text_response)
    user_input = text_response  # override text area with voice answer

# Feedback button
if st.button("Get Feedback"):
    if not user_input.strip():
        st.warning("Please write or record your answer first.")
    else:
        st.session_state[SESSION_KEY].append({"role": "user", "content": user_input})
        if api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=st.session_state[SESSION_KEY],
                    max_tokens=500,
                    temperature=0.2
                )
                reply = response.choices[0].message["content"]
            except Exception as e:
                reply = f"Error: {e}"
        else:
            reply = ("MOCK FEEDBACK:\n"
                     "- Good start but missing metrics.\n"
                     "- Improvements: Add numbers, clarify your role, tie to company goals.\n"
                     "- Score: 6/10\n"
                     "- Follow-up: What would you do differently next time?")
        st.session_state[SESSION_KEY].append({"role": "assistant", "content": reply})
        st.rerun()

# Next question button
if st.button("Next Question"):
    st.session_state[SESSION_KEY].append({"role": "user", "content": "Please ask the next interview question."})
    if api_key:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=st.session_state[SESSION_KEY],
                max_tokens=150,
                temperature=0.3
            )
            next_q = response.choices[0].message["content"]
        except Exception as e:
            next_q = f"Error: {e}"
    else:
        next_q = "MOCK QUESTION: Tell me about a time you handled conflicting priorities."
    st.session_state[SESSION_KEY].append({"role": "assistant", "content": next_q})

    # Play audio version of question (TTS)
    try:
        tts_audio = text_to_speech_elevenlabs(next_q, os.getenv("ELEVENLABS_API_KEY"))
        st.audio(tts_audio, format="audio/mp3")
    except:
        pass

    st.rerun()

# Show conversation history
st.markdown("### Conversation History")
for msg in st.session_state[SESSION_KEY]:
    if msg["role"] == "system":
        st.write(f"**SYSTEM:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.info(msg["content"])
    else:
        st.write(f"**You:** {msg['content']}")

# Save & load session
if st.button("💾 Save Session"):
    save_session(st.session_state[SESSION_KEY])
    st.success("Session saved successfully!")

    # Offer download
    json_data = export_session()
    st.download_button("⬇️ Download Session", json_data, "session.json", "application/json")

uploaded = st.file_uploader("⬆️ Upload previous session (JSON)", type="json")
if uploaded:
    if import_session(uploaded):
        st.success("Session imported successfully!")
        st.rerun()
