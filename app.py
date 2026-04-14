import streamlit as st
import google.generativeai as genai
import sqlite3
from streamlit_mic_recorder import speech_to_text

# 1. Page Config
st.set_page_config(page_title="AI Financial Assistant", page_icon="🎙️")
st.title("🎙️ AI Financial Voice Assistant")

# 2. Secure API & Model Discovery
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API Key not found in secrets.toml!")
except Exception as e:
    st.error(f"Configuration Error: {e}")

def find_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not models:
            return None
        
        # Priority list for models
        for target in ["models/gemini-1.5-flash", "models/gemini-pro"]:
            if any(target in m for m in models):
                return genai.GenerativeModel(target)
        return genai.GenerativeModel(models[0])
    except Exception:
        return None

model = find_working_model()

# 3. Database Setup (Fixed Syntax)
def init_db():
    conn = sqlite3.connect('calc_history.db', check_same_thread=False)
    cursor = conn.cursor()
    # Table to store history for Data Analysis
    cursor.execute('''CREATE TABLE IF NOT EXISTS history
                     (method TEXT, question TEXT, answer TEXT)''')
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# 4. User Interface
tab1, tab2, tab3 = st.tabs(["🎤 Voice", "⌨️ Text", "📜 History"])

user_query = None

with tab1:
    st.subheader("Speak your financial question")
    # This captures audio and converts it to text
    voice_text = speech_to_text(start_prompt="Click to Speak", stop_prompt="Stop Recording", key='speech')
    if voice_text:
        user_query = voice_text
        st.info(f"Detected: {user_query}")

with tab2:
    st.subheader("Type your question")
    typed_query = st.text_input("e.g., 'Calculate the ROI on $5000 over 2 years at 7%'")
    if typed_query:
        user_query = typed_query

# 5. Execution Logic
if user_query and model:
    with st.spinner("AI analyzing..."):
        try:
            response = model.generate_content(f"You are a financial assistant. Solve: {user_query}")
            answer = response.text
            st.success(answer)

            # Log to SQL Database
            cursor.execute("INSERT INTO history (method, question, answer) VALUES (?, ?, ?)", 
                           ("Voice" if user_query == voice_text else "Text", user_query, answer))
            conn.commit()
        except Exception as e:
            st.error(f"AI Error: {e}")

with tab3:
    st.subheader("Recent Calculations")
    history = cursor.execute("SELECT * FROM history ORDER BY rowid DESC LIMIT 5").fetchall()
    for item in history:
        with st.expander(f"{item[0]}: {item[1][:50]}..."):
            st.write(f"**Question:** {item[1]}")
            st.write(f"**Answer:** {item[2]}")
