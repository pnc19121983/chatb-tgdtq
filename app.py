import streamlit as st

# --- Cấu hình trang ---
st.set_page_config(page_title="Chatbot NotebookLM", layout="wide")

# --- Tiêu đề ---
st.title("🤖 NotebookLM Chatbot nhúng trong Streamlit")

# --- Link NotebookLM của bạn ---
notebooklm_url = "https://notebooklm.google.com/notebook/d0d6a3bf-9388-4868-8bfa-6469a26f4b78?authuser=0"

# --- Hiển thị trong iframe ---
st.components.v1.iframe(src=notebooklm_url, height=800, width=1200)
