import os
import json
import streamlit as st
from prompts import SYSTEM_PROMPT_TEMPLATE
import openai

# NEW IMPORTS
from voice_input import transcribe_audio
from voice_output import text_to_speech_elevenlabs
from session_manager import save_session, load_session

def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass
    return api_key

st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="wide")
st.title("🎯 AI Interview Coach — Live Demo (Text + Voice)")

api_key = get_api_key()
if api_key:
    openai.api_key = api_key
else:
    st.warning("No OPENAI_API_KEY found. Set it to call the OpenAI API. The app will show MOCK responses without a key.")

# Load previous session if available
if "chat" not in st.session_state:
    st.session_state.chat = load_session() or [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(role="SDE", type="Behavioral")}
    ]

role = st.selectbox("Role", ["SDE", "Data Analyst", "ML Engineer", "Product Manager"], index=0, key="role")
interview_type = st.selectbox("Interview Type", ["Behavioral", "Technical", "HR"], index=0, key="interview_type")

# Show the current question clearly
last_msg = st.session_state.chat[-1]["content"] if st.session_state.chat and st.session_state.chat[-1]["role"] == "assistant" else None
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
        st.session_state.chat.append({"role": "user", "content": user_input})
        if api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=st.session_state.chat,
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
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()  # modern replacement

# Next question button
if st.button("Next Question"):
    st.session_state.chat.append({"role": "user", "content": "Please ask the next interview question."})
    if api_key:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=st.session_state.chat,
                max_tokens=150,
                temperature=0.3
            )
            next_q = response.choices[0].message["content"]
        except Exception as e:
            next_q = f"Error: {e}"
    else:
        next_q = "MOCK QUESTION: Tell me about a time you handled conflicting priorities."
    st.session_state.chat.append({"role": "assistant", "content": next_q})

    # Play audio version of question (TTS)
    try:
        tts_audio = text_to_speech_elevenlabs(next_q, os.getenv("ELEVENLABS_API_KEY"))
        st.audio(tts_audio, format="audio/mp3")
    except:
        pass

    st.rerun()  # modern replacement

# Show history
st.markdown("### Conversation History")
for msg in st.session_state.chat:
    if msg["role"] == "system":
        st.write(f"**SYSTEM:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.info(msg["content"])
    else:
        st.write(f"**You:** {msg['content']}")

# Save session
if st.button("💾 Save Session"):
    save_session(st.session_state.chat)
    st.success("Session saved successfully!")
