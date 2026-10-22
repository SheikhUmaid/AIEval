import streamlit as st
from llm import ask_ai
import os

st.set_page_config(page_title="AI-Powered Text Summarizer", page_icon="📝", layout="centered")

st.title("📝 AI-Powered Text Summarizer")
st.write("Enter any article, paragraph, or document below and get a concise AI-generated summary.")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key_input = st.text_input(
        "Gemini API Key (optional if in .env)",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Enter your Google Gemini API key if not configured in the .env file."
    )
    if api_key_input:
        st.session_state.gemini_api_key = api_key_input
        os.environ["GEMINI_API_KEY"] = api_key_input
    
    summary_length = st.selectbox(
        "Summary Style / Length",
        ["Concise (3-4 bullet points)", "Executive Brief (1 short paragraph)", "Detailed Overview"],
        index=0
    )

# 1. Create a text area where users can enter a paragraph or article
user_text = st.text_area(
    "Paste your text here:",
    height=250,
    placeholder="Paste a news article, research excerpt, meeting notes, or any lengthy text to summarize..."
)

# 2. Add a button labelled "Summarize"
if st.button("Summarize"):
    # 5. If the user clicks the button without entering text, display a warning
    if not user_text.strip():
        st.warning("Please enter some text to summarize.")
    else:
        # 3. Send the entered text to Gemini using the existing ask_ai() function from llm.py
        with st.spinner("Generating summary..."):
            prompt = f"""
            You are an expert editor and summarizer.
            Please summarize the following text using the specified style: {summary_length}.
            Keep the key facts, numbers, dates, and conclusions clear and accurate.

            TEXT:
            {user_text}
            """
            summary = ask_ai(prompt)

        # 4. Display the generated summary on the webpage
        st.subheader("Summary")
        st.markdown(summary)

