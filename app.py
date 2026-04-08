import streamlit as st
import google.generativeai as genai

# Use Streamlit's "secrets" to hide your API key
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

st.set_page_config(page_title="AI Smart Calc", page_icon="🧮")
st.title("🧮 AI Powered Calculator")
st.write("Ask anything: 'Calculate my BMI', 'Split a $150 bill 3 ways', or 'Physics trajectory'.")

user_input = st.text_input("Enter your calculation:", placeholder="e.g. What is 15% tip on $84.50?")

if user_input:
    with st.spinner('Calculating...'):
        # We tell the AI to act as a precise calculator
        prompt = f"Solve this math/logic problem step-by-step: {user_input}. End with 'Final Answer: [result]'"
        response = model.generate_content(prompt)
        st.info(response.text)
