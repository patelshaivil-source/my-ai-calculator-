import streamlit as st
import google.generativeai as genai

# 1. API Setup
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. High-Quality "Cyber-Luxury" Design
st.set_page_config(page_title="cAlsI Intelligence", layout="centered")

st.markdown("""
    <style>
    /* Dark Matrix Background */
    .stApp {
        background: radial-gradient(circle at center, #0a1f0a 0%, #000000 100%);
        color: #00ff41;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Neumorphic 3D Card */
    .luxury-card {
        background: rgba(0, 0, 0, 0.6);
        border: 2px solid #00ff41;
        border-radius: 25px;
        padding: 50px;
        box-shadow: 0 0 15px #00ff41, inset 0 0 10px #00ff41;
        margin-top: 50px;
        text-align: center;
    }

    /* Animated Title */
    .glitch {
        font-size: 70px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 10px;
        text-shadow: 2px 2px #000, 0 0 20px #00ff41;
    }

    /* Result Display */
    .result-box {
        background: rgba(0, 255, 65, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-top: 30px;
        border-left: 5px solid #00ff41;
        font-size: 40px;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. App UI
st.markdown('<div class="luxury-card">', unsafe_allow_html=True)
st.markdown('<div class="glitch">cAlsI</div>', unsafe_allow_html=True)
st.write("### ADVANCED NUMERICAL ENGINE")

# New 2026 Native Audio Input
audio_data = st.audio_input("INITIATE VOICE COMMAND")

if audio_data:
    with st.status("Computing...", expanded=False) as status:
        try:
            # Explicit instructions for high-end behavior
            response = model.generate_content([
                "Identify as cAlsI. Be precise. Return ONLY the numerical result and a 1-sentence technical explanation. Use green emojis.",
                {"mime_type": "audio/wav", "data": audio_data.read()}
            ])
            
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.write(f"📟 {response.text}")
            st.markdown('</div>', unsafe_allow_html=True)
            status.update(label="Computation Complete", state="complete")
            
        except Exception as e:
            st.error(f"SYSTEM FAILURE: {e}")

st.markdown('</div>', unsafe_allow_html=True)
