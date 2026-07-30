import os
from flask import Flask, request, jsonify
from flask_cors import CORS # Nếu bạn cần gọi từ frontend khác port
import google.generativeai as genai
from rag_engine import RAGEngine
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

app = Flask(__name__)
CORS(app) # Cho phép gọi API từ mọi nguồn (để test local)

# Cấu hình Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Sử dụng model gemini-1.5-flash (Nhanh, rẻ, xử lý text tốt)
model = genai.GenerativeModel('models/gemini-pro')

# Khởi tạo Engine xử lý
rag = RAGEngine()

@app.route('/summarize', methods=['POST'])
def summarize_endpoint():
    """
    API nhận đường dẫn file PDF, thực hiện RAG và gọi AI.
    """
    data = request.get_json()
    pdf_path = data.get('pdf_path')
    day_info = data.get('day_info', 'Slide hiện tại')

    if not pdf_path:
        return jsonify({"success": False, "error": "Thiếu đường dẫn file PDF"}), 400

    # Bước 1: Đọc PDF
    print(f"⏳ Đang đọc file: {pdf_path}...")
    raw_text = rag.extract_text_from_pdf(pdf_path)

    # Kiểm tra nếu file bị lỗi (Ví dụ: không tìm thấy file)
    if "Lỗi" in raw_text:
        return jsonify({"success": False, "error": raw_text}), 400

    # Bước 2: Chunking (RAG Engine xử lý)
    context = rag.create_rag_context(raw_text)

    # Bước 3: Tạo Prompt với luật chống Hallucination
    final_prompt = rag.build_summary_prompt(context, day_info)

    # Bước 4: Gọi AI (Lời gọi AI thật bắt buộc ở CP3)
    print("⏳ Đang gọi Gemini API để tóm tắt...")
    try:
        response = model.generate_content(final_prompt)
        summary_text = response.text

        # Bước 5: Hậu kiểm (Post-processing) - Check Hallucination đơn giản
        # Nếu câu trả lời có các từ như "Theo tôi", "Có lẽ", mà không có dẫn chứng trang -> cảnh báo
        if "Theo tôi" in summary_text and "[Trang" not in summary_text:
            summary_text += "\n\n*(⚠️ Lưu ý: AI có thể đã thêm nhận định cá nhân. Vui lòng đối chiếu slide gốc kỹ càng trước khi dùng.)*"

        return jsonify({
            "success": True, 
            "summary": summary_text,
            "raw_context_length": len(context)
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi khi gọi AI API: {str(e)}"}), 500

# Đoạn này dùng để tự test API mà không cần Frontend
# Thay thế toàn bộ phần dưới cùng của file bằng đoạn này:
if __name__ == '__main__':
    print("🚀 Server backend đang chạy tại http://127.0.0.1:5000")
    print("⚠️ Đang chờ yêu cầu từ Frontend hoặc Postman...")
    app.run(debug=True, port=5000)