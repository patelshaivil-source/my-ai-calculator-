import streamlit as st
import google.generativeai as genai
import sqlite3
from streamlit_mic_recorder import speech_to_text

# 1. Page Config
st.set_page_config(page_title="AI Financial Assistant", page_icon="🎙️")
st.title("🎙️ AI Financial Voice Assistant")

# 2. Secure API & Model Discovery
# Note: Ensure your GEMINI_API_KEY is in .streamlit/secrets.toml
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Key not found. Please check your secrets.toml file.")

def find_working_model():
    try:
        # Check what models your specific key is authorized for
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

        if not models:
            st.error("No models found! Check your API Key permissions in Google AI Studio.")
            return None

        # Try to find the best one from the list
        for target in ["models/gemini-1.5-flash", "models/gemini-pro", "models/chat-bison-001"]:
            if any(target in m for m in models):
                return genai.GenerativeModel(target)

        # Fallback to the first available model in the list
        return genai.GenerativeModel(models[0])
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

model = find_working_model()

# 3. Database Setup
def init_db():
    conn = sqlite3.connect('calc_history.db', check_same_thread=False)
    cursor = conn.cursor()
    # Create the history table for your Data Analysis requirements
    cursor.execute('''CREATE TABLE IF NOT EXISTS history
                     (method TEXT, question TEXT, answer TEXT)''')
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# 4. User Interface Tabs
tab1, tab2, tab3 = st.tabs(["🎤 Voice Recognition", "⌨️ Text Input", "📜 History"])

user_query = None

with tab1:
    st.subheader("Speak your math or financial problem")
    # This component handles the microphone input
    text = speech_to_text(start_prompt="Click to Speak", stop_prompt="Stop Recording", key='speech')
    if text:
        user_query = text
        st.write(f"**Detected Voice:** {user_
