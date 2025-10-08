import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# === Cấu hình Gemini (đảm bảo đã lưu GEMINI_API_KEY trong Streamlit Secrets) ===
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# === Cấu hình model ===
MODEL_NAME = "models/gemini-2.5-flash"  # dạng chuẩn để gọi Gemini 2.5


# === Hàm đọc nội dung từ tất cả PDF/TXT trong thư mục hiện tại ===
def load_docs_text(max_chars=30000):
    """
    Đọc toàn bộ file .pdf và .txt cùng cấp với app.py
    Trả về (all_text, file_list).
    Giới hạn tổng số ký tự trả về bằng max_chars để tránh gửi context quá dài.
    """
    text = ""
    files = []
    for filename in sorted(os.listdir(".")):
        if filename.lower().endswith((".pdf", ".txt")):
            files.append(filename)
            try:
                if filename.lower().endswith(".pdf"):
                    reader = PdfReader(filename)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                else:
                    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                        text += f.read() + "\n"
            except Exception as e:
                text += f"\n[⚠️ Không đọc được {filename}: {e}]\n"

    if len(text) > max_chars:
        head = text[: max_chars // 2]
        tail = text[-(max_chars // 2) :]
        text = head + "\n\n... (nội dung bị cắt vì quá dài) ...\n\n" + tail

    return text, files


# === Helper: trích text từ response ===
def extract_text_from_response(resp):
    if not resp:
        return ""
    if hasattr(resp, "text") and resp.text:
        return resp.text
    try:
        return resp.candidates[0].content.parts[0].text
    except Exception:
        try:
            return resp.candidates[0].output[0].content[0].text
        except Exception:
            return str(resp)


# === Mẫu định dạng bắt buộc ===
OUTPUT_TEMPLATE = """Câu trả lời phải ngắn gọn, rõ ràng, theo định dạng chuẩn thống nhất:
---
**📌 Cấp có thẩm quyền:** [Tỉnh/Xã]

**📄 Căn cứ pháp lý:**
- [Số văn bản, Điều, Khoản, Điểm, trích nguyên văn nếu cần]

**✅ Kết luận:**
- [Khẳng định cấp có thẩm quyền và người đại diện theo văn bản]
---
"""


# === Giao diện Streamlit ===
st.set_page_config(page_title="Sở Giáo dục và Đào tạo Tuyên Quang", layout="wide")
st.title("Sở Giáo dục và Đào tạo Tuyên Quang")

with st.expander("📂 Danh sách tài liệu được nạp"):
    docs_text, file_list = load_docs_text()
    if file_list:
        st.write("Ứng dụng đang dùng các file:")
        for f in file_list:
            st.write("- " + f)
    else:
        st.warning("Không tìm thấy file PDF/TXT nào trong thư mục hiện tại.")

st.info("✅ Đã nạp xong tài liệu nội bộ." if file_list else "⚠️ Vui lòng đặt file PDF/TXT cùng cấp với app.py rồi reload.")


# === Ô nhập câu hỏi ===
user_input = st.text_area("💬 Nhập câu hỏi của bạn:", height=120)

col1, col2 = st.columns([1, 4])
with col1:
    send_btn = st.button("Gửi câu hỏi")
with col2:
    st.write("")


# === Khi người dùng nhấn Gửi ===
if send_btn:
    if not user_input.strip():
        st.warning("⚠️ Vui lòng nhập câu hỏi.")
    else:
        status = st.empty()
        status.info("⏳ Đang xử lý...")

        # === Prompt kiểm soát hành vi ===
        final_prompt = f"""
Bạn là trợ lý hành chính chuyên phân tích văn bản pháp lý.
⚠️ QUY TẮC BẮT BUỘC:
- Chỉ được phép sử dụng thông tin có trong tài liệu dưới đây.
- Tuyệt đối KHÔNG dùng kiến thức nền hoặc thông tin từ Internet.
- Nếu không tìm thấy thông tin phù hợp, hãy trả lời:
  "Không tìm thấy thông tin trong các tài liệu được cung cấp."
- Câu trả lời PHẢI theo đúng mẫu định dạng sau.

{OUTPUT_TEMPLATE}

-------------------
📚 Dưới đây là toàn bộ nội dung tài liệu nội bộ:
{docs_text}
-------------------

Người dùng hỏi: {user_input}

👉 Hãy trả lời chính xác, ngắn gọn, đúng mẫu, trích dẫn cụ thể điều khoản nếu có.
        """

        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(final_prompt)
            answer = extract_text_from_response(response)

            status.success("✅ Hoàn thành.")
            st.markdown("### 🧾 Kết quả (theo mẫu):")
            st.markdown(answer)

        except Exception as e:
            status.error("❌ Có lỗi khi gọi Gemini API.")
            st.error(f"Lỗi chi tiết: {e}")
