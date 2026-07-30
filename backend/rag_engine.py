import PyPDF2
import os

class RAGEngine:
    def __init__(self):
        # Đường dẫn tới thư mục prompts (Tính từ thư mục gốc dự án, hoặc bạn có thể để đường dẫn tuyệt đối)
        # Ở đây tôi giả định bạn chạy Python từ thư mục backend/
        self.prompt_dir = "../prompts" 

    def extract_text_from_pdf(self, pdf_path):
        # ... (Giữ nguyên code cũ) ...
        full_text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        full_text += f"[Trang {page_num + 1}]\n{text}\n\n"
            return full_text.strip()
        except Exception as e:
            return f"Lỗi khi đọc PDF: {str(e)}"

    def create_rag_context(self, full_text, max_chunk_size=3000):
        # ... (Giữ nguyên code cũ) ...
        chunks = []
        lines = full_text.split('\n')
        current_chunk = ""
        for line in lines:
            if len(current_chunk) + len(line) < max_chunk_size:
                current_chunk += line + "\n"
            else:
                chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
        if current_chunk:
            chunks.append(current_chunk.strip())
        return "\n\n".join(chunks)

    def build_summary_prompt(self, slide_content, day_info="Day 5"):
        """
        Bước 3: Đọc Prompt từ file thay vì hardcode.
        """
        # Đọc file summarize_prompt.txt
        prompt_path = os.path.join(self.prompt_dir, "summarize_prompt.txt")
        
        # Nếu file prompt không tồn tại, dùng fallback (Prompt cũ hardcode) để tránh crash
        if not os.path.exists(prompt_path):
            print("⚠️ Không tìm thấy file prompt, đang dùng Prompt mặc định trong code...")
            return self._get_fallback_prompt(slide_content, day_info)
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Thay thế biến {slide_content} bằng nội dung thực tế
        final_prompt = template.replace("{slide_content}", slide_content)
        return final_prompt

    def _get_fallback_prompt(self, slide_content, day_info):
        """
        Hàm dự phòng nếu không đọc được file text (để code không bị lỗi)
        """
        return f"""
        Bạn là Trợ lý học tập. Tóm tắt slide {day_info} thành 5-7 ý:
        ---
        {slide_content}
        ---
        Tuyệt đối không thêm kiến thức ngoài slide. Kèm 3 câu hỏi kiểm tra.
        """