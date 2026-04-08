import streamlit as st
import google.generativeai as genai

# 1. API Configuration
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Green & Black "Matrix Luxury" Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #000000 0%, #062106 100%);
    }
    .glass-card {
        background: rgba(0, 255, 0, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid #00ff00;
        padding: 40px;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        text-align: center;
        color: #00ff00;
    }
    h1 { color: #00ff00; font-family: 'Courier New', monospace; font-weight: bold; }
    p { color: #00ff00; }
    /* This changes the microphone button color to green */
    button {
        background-color: #00ff00 !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. The Layout
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.title("cAlsI")
st.write("Precision Numerical Intelligence")

# 4. Voice Input
audio_data = st.audio_input("Speak Command")

if audio_data:
    with st.spinner('Calculating...'):
        try:
            # We explicitly tell cAlsI to respond only in numbers or short formulas
            response = model.generate_content([
                "You are cAlsI. Provide only numerical answers and short, direct solutions. No conversational filler.",
                {"mime_type": "audio/wav", "data": audio_data.read()}
            ])
            
            st.markdown(f"## Result:")
            # We display the result in a large, bold font for high visibility
            st.markdown(f"<h1 style='font-size: 60px;'>{response.text}</h1>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"System Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
