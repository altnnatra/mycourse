import streamlit as st
import pandas as pd
import requests
import json
import subprocess
import os
from dotenv import load_dotenv

# === CONFIGURATION ===
load_dotenv()
ANTHROPIC_API_URL = os.getenv("ANTHROPIC_API_URL", "https://api.anthropic.com/v1/messages")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LMSTUDIO_API_URL = "http://localhost:1234/v1/chat/completions"
CSV_FILE = "courses.csv"

# === Load CSV Data ===
@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

# === Query Claude (Anthropic) ===
def query_anthropic(prompt):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 1024,
        "system": "You are a helpful assistant.",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()['content'][0]['text']
    else:
        return f"[Anthropic Error {response.status_code}] {response.text}"

# === Query Ollama (Local LLM) ===
def query_ollama(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "mistral",
        "stream": False,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post("http://localhost:11434/api/chat", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"[Ollama Error {response.status_code}] {response.text}"
    except Exception as e:
        return f"❌ Error using Ollama: {e}"

# === STREAMLIT APPLICATION ===
st.set_page_config(page_title="Offerings Scraper UI", layout="wide")
st.title("📚 Offerings Scraper - CUD")

llm_choice = st.radio("Choose an LLM Model:", ["Claude (Anthropic)", "Local (Ollama)"])

# === State control for login popup ===
if "show_login" not in st.session_state:
    st.session_state.show_login = False

# === Initial button to show login form ===
if st.button("🔄 Scrape courses from portal"):
    st.session_state.show_login = True

# === Login form with semester and year of study ===
if st.session_state.show_login:
    st.subheader("🔐 Enter CUD Portal Credentials and Semester Info")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    semester = st.selectbox("📅 Select Semester", ["SP 2024-25", "SU 1 2024-25", "FA 2025-26"])
    year_of_study = st.text_input("🎓 Enter Year of Study (e.g., 1, 2, 3, 4)")

    if st.button("✅ Submit and Run Scraper"):
        if username and password:
            with st.spinner("Running browser agent..."):
                try:
                    subprocess.run(
                        ["python", "scrape_agent.py", username, password, semester, year_of_study],
                        check=True
                    )
                    st.success("✅ Courses scraped successfully!")
                    st.session_state.show_login = False
                except Exception as e:
                    st.error(f"❌ Scraping error: {e}")
        else:
            st.warning("Please enter both username and password.")

# === Display CSV Data ===
if os.path.exists(CSV_FILE):
    df = load_csv(CSV_FILE)
    st.subheader("Course Table Preview:")
    st.dataframe(df)

    user_query = st.text_area("💬 Ask something about the courses:", placeholder="e.g., Show me all courses taught by Dr. Said Elnaffar")

    if st.button("Run Query") and user_query:
        csv_text = df.to_csv(index=False)
        prompt = f"""
You are a helpful assistant. Here is a CSV file containing university course data:

{csv_text}

Each course has a code like "BCS101", "BCS206", etc. The **year of study** can be inferred from the first digit after the department prefix (e.g., "101" = 1st year, "206" = 2nd year, "311" = 3rd year, and so on).

Please analyze the data and answer the user's query **based only on the information in the table above**.

User query: "{user_query}"

In your response:
- Include insights from the data only.
- If needed, infer the year of study using the course code pattern.
- Be accurate, concise, and use bullet points or markdown formatting.
"""

        with st.spinner("Thinking..."):
            if llm_choice == "Claude (Anthropic)":
                answer = query_anthropic(prompt)
            else:
                answer = query_ollama(prompt)

        st.markdown("### 🤖 LLM Response")
        st.write(answer)
else:
    st.info("👈 Please click 'Scrape courses' or upload 'courses.csv' manually to begin.")
