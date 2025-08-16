
import os
import json
import streamlit as st
from prompts import SYSTEM_PROMPT_TEMPLATE
import openai

def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass
    return api_key

st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="wide")
st.title("🎯 AI Interview Coach — Live Demo (Text mode)")

api_key = get_api_key()
if api_key:
    openai.api_key = api_key
else:
    st.warning("No OPENAI_API_KEY found. Set it to call the OpenAI API. The app will show MOCK responses without a key.")

role = st.selectbox("Role", ["SDE", "Data Analyst", "ML Engineer", "Product Manager"], index=0, key="role")
interview_type = st.selectbox("Interview Type", ["Behavioral", "Technical", "HR"], index=0, key="interview_type")

if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(role=role, type=interview_type)}]

user_input = st.text_area("Your answer", height=200)

if st.button("Get Feedback"):
    if not user_input.strip():
        st.warning("Please write your answer first.")
    else:
        st.session_state.chat.append({"role":"user","content":user_input})
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
        st.session_state.chat.append({"role":"assistant","content":reply})
        st.experimental_rerun()

if st.button("Next Question"):
    st.session_state.chat.append({"role":"user","content":"Please ask the next interview question."})
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
    st.session_state.chat.append({"role":"assistant","content":next_q})
    st.experimental_rerun()

st.markdown("### Conversation History")
for msg in st.session_state.chat:
    if msg["role"] == "system":
        st.write(f"**SYSTEM:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.info(msg["content"])
    else:
        st.write(f"**You:** {msg['content']}")
