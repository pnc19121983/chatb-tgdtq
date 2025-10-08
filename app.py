import streamlit as st

st.set_page_config(page_title="Chatbot NotebookLM", layout="wide")
st.title("🤖 NotebookLM Chatbot")

notebooklm_url = "https://notebooklm.google.com/notebook/d0d6a3bf-9388-4868-8bfa-6469a26f4b78?authuser=0"

st.info("Google không cho phép nhúng NotebookLM trong iframe. Hãy mở bằng nút bên dưới 👇")

st.markdown(f"[🧠 Mở NotebookLM trong tab mới]({notebooklm_url})", unsafe_allow_html=True)
