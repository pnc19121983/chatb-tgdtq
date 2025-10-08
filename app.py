import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# === Cấu hình Gemini (đảm bảo đã lưu GEMINI_API_KEY trong Streamlit Secrets) ===
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# === Cấu hình model (thay đổi nếu bạn có model khác) ===
MODEL_NAME = "models/gemini-2.5-flash"  # nếu cần đổi, hãy để dạng "models/..."


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
        if filename.lower().endswith(".pdf") or filename.lower().endswith(".txt"):
            files.append(filename)
            try:
                if filename.lower().endswith(".pdf"):
                    reader = PdfReader(filename)
                    # Có thể có trường hợp page.extract_text() trả None, nên guard
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                else:  # .txt
                    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                        text += f.read() + "\n"
            except Exception as e:
                # Ghi chú lỗi vào text để biết file nào lỗi
                text += f"\n[⚠️ Không đọc được {filename}: {e}]\n"

    # Cắt ngắn nếu quá dài (giữ phần đầu và phần cuối để cố gắng bảo toàn thông tin)
    if len(text) > max_chars:
        head = text[: max_chars // 2]
        tail = text[-(max_chars // 2) :]
        text = head + "\n\n... (nội dung bị cắt vì quá dài) ...\n\n" + tail

    return text, files


# === Helper: trích text từ response (tương thích nhiều dạng trả về) ===
def extract_text_from_response(resp):
    # Thử truy cập attribute phổ biến
    if not resp:
        return ""
    if hasattr(resp, "text") and resp.text:
        return resp.text
    # Một số phiên bản trả về cấu trúc phức tạp hơn:
    try:
        # resp.candidates[0].content.parts[0].text
        return resp.candidates[0].content.parts[0].text
    except Exception:
        try:
            # resp.candidates[0].output[0].content[0].text
            return resp.candidates[0].output[0].content[0].text
        except Exception:
            return str(resp)


# === Mẫu định dạng bắt buộc (nguyên văn theo yêu cầu của bạn) ===
OUTPUT_TEMPLATE = """Câu trả lời phải ngắn gọn, rõ ràng, theo định dạng chuẩn thống nhất:
---
**📌 Cấp có thẩm quyền:** [Tỉnh/Xã] \n
**📄 Căn cứ pháp lý:** \n
- [Số văn bản, Điều, Khoản, Điểm, trích nguyên văn nếu cần] \n
**✅ Kết luận:** \n
- [Khẳng định cấp có thẩm quyền và người đại diện theo văn bản]
"""

# === Streamlit UI ===
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

st.info("Đã nạp xong tài liệu nội bộ." if file_list else "Vui lòng đặt file PDF/TXT cùng cấp với app.py rồi reload.")

# Ô nhập câu hỏi
user_input = st.text_area("💬 Nhập câu hỏi của bạn:", height=120)

col1, col2 = st.columns([1, 4])
with col1:
    send_btn = st.button("Gửi câu hỏi")
with col2:
    st.write("")

if send_btn:
    if user_input.strip() == "":
        st.warning("⚠️ Vui lòng nhập câu hỏi.")
    else:
        # Hiển thị trạng thái
        status = st.empty()
        status.info("⏳ Đang xử lý...")

        # Tạo prompt: kết hợp template + nội dung tài liệu + yêu cầu trả lời chính xác theo mẫu
        # Giữ docs_text ngắn gọn (hàm load_docs_text đã cắt nếu quá dài)
        final_prompt = (
            OUTPUT_TEMPLATE
            + "\n\n"
            + "Dưới đây là nội dung các tài liệu nội bộ (dùng để trích dẫn/căn cứ):\n"
            + "-------------------\n"
            + docs_text
            + "\n-------------------\n"
            + f"Yêu cầu: Người dùng hỏi: {user_input}\n"
            + "HÃY TRẢ LẠI CHÍNH XÁC THEO ĐÚNG MẪU TRÊN. Chỉ trả lời theo mẫu, KHÔNG thêm phần giải thích hoặc văn phong khác."
        )

        try:
            # Gọi model
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(final_prompt)
            answer = extract_text_from_response(response)

            # Hiển thị kết quả (giữ nguyên định dạng markdown)
            status.success("✅ Hoàn thành.")
            st.markdown("### 🧾 Kết quả (theo mẫu):")
            # hiển thị raw markdown; model được yêu cầu trả theo mẫu, nên show trực tiếp
            st.markdown(answer)
        except Exception as e:
            # Hiện thông báo lỗi chung (chi tiết lỗi được ghi trong logs của Streamlit Cloud)
            status.error("❌ Có lỗi khi gọi API. Xem logs để biết chi tiết.")
            st.error(f"Lỗi: {e}")
