import streamlit as st
import google.generativeai as genai

# 1. API Configuration
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
# Using the high-performance 2026 model
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Luxury Glassmorphism Styling
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #1a1a2e 0%, #020205 100%);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 40px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        text-align: center;
    }
    h1 { color: #ffffff; font-weight: 200; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

# 3. The 3D UI Layout
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.title("S O P H I A")
st.write("Your Luxury AI Concierge")

# 4. Voice Input Widget (New for 2026)
audio_data = st.audio_input("Speak to Sophia")

if audio_data:
    with st.spinner('Refining response...'):
        try:
            # We send the audio bytes directly to Gemini 2.5
            response = model.generate_content([
                "You are Sophia, a sophisticated luxury concierge. Speak with elegance and precision.",
                {"mime_type": "audio/wav", "data": audio_data.read()}
            ])
            
            st.markdown(f"### ✨ Sophia's Response:")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"Concierge unavailable: {e}")

st.markdown('</div>', unsafe_allow_html=True)
