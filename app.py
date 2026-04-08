import streamlit as st
import google.generativeai as genai
import time

# 1. Setup - Pulls your secret key from Streamlit settings
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Using the most stable 2026 model
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
except Exception as e:
    st.error("Missing API Key. Please check your Streamlit Secrets.")

# 2. UI Styling
st.set_page_config(page_title="AI Smart Calc", page_icon="🧮")
st.title("🧮 AI Powered Calculator")
st.write("Ask anything: 'Calculate my BMI', 'Split a $150 bill 3 ways', or 'Physics trajectory'.")

user_input = st.text_input("Enter your calculation:", placeholder="e.g. What is 15% tip on $84.50?")

# 3. Logic with "Retry" fix for the Resource error
if user_input:
    with st.spinner('Calculating...'):
        prompt = f"Solve this math/logic problem step-by-step: {user_input}. End with 'Final Answer: [result]'"
        
        success = False
        # It will try up to 3 times if the server is busy
        for attempt in range(3):
            try:
                response = model.generate_content(prompt)
                st.info(response.text)
                success = True
                break 
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    st.warning(f"Server is busy. Retrying in {attempt + 2} seconds...")
                    time.sleep(attempt + 2)
                else:
                    st.error(f"An error occurred: {e}")
                    break
        
        if not success:
            st.error("Google's free servers are currently overloaded. Please try again in a minute.")
