import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# === Cấu hình Gemini ===
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# === Hàm đọc nội dung từ tất cả PDF/TXT trong thư mục hiện tại ===
def load_docs_text():
    text = ""
    for filename in os.listdir("."):
        if filename.endswith(".pdf"):
            reader = PdfReader(filename)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif filename.endswith(".txt"):
            with open(filename, "r", encoding="utf-8") as f:
                text += f.read() + "\n"
    return text

# === Giao diện Streamlit ===
st.set_page_config(page_title="NotebookLM Chatbot", layout="wide")
st.title("🤖 Chatbot kiểu NotebookLM (Gemini)")

st.info("Đang tải tài liệu PDF/TXT trong thư mục hiện tại...")
docs_text = load_docs_text()
st.success("✅ Đã nạp xong tài liệu nội bộ.")

# Ô nhập câu hỏi
user_input = st.text_area("💬 Nhập câu hỏi của bạn:", height=100)
if st.button("Gửi câu hỏi"):
    if user_input.strip() == "":
        st.warning("⚠️ Vui lòng nhập câu hỏi.")
    else:
        st.markdown("⏳ **Đang xử lý...**")

        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        Bạn là trợ lý kiểu NotebookLM.
        Dưới đây là nội dung tài liệu nội bộ:
        -------------------
        {docs_text}
        -------------------
        Câu hỏi: {user_input}
        Hãy trả lời chi tiết, chính xác, có dẫn chứng từ nội dung tài liệu.
        """

        response = model.generate_content(prompt)
        st.markdown("### 🧠 Trả lời:")
        st.write(response.text)
