# AI SPEC — Lát cắt Tóm tắt Bài giảng 
Hướng: [ ] A — VLearn  [x] B — Trợ lý Học viên  [ ] C — Làn mở  
Loại: [x] Tính năng mới  [ ] Tối ưu tính năng có sẵn  

---

## §1. User & Job
- **Job executor + workflow:** 
  - **Học viên:** Xem lại bài giảng $\rightarrow$ Đọc Slide & Transcript $\rightarrow$ Tóm tắt ý chính & Đặt câu hỏi thắc mắc.
  - **Trợ giảng (TA):** Tiếp nhận câu hỏi $\rightarrow$ Tra cứu bài giảng $\rightarrow$ Soạn câu trả lời $\rightarrow$ Phản hồi học viên.
- **Core JTBD:** Khi tham gia lớp học quy mô lớn, học viên muốn nhanh chóng nắm bắt các kiến thức trọng tâm từ slide/video bài giảng và nhận được giải đáp chính xác cho các thắc mắc về lỗi kỹ thuật/lý thuyết mà không phải chờ đợi quá lâu.
- **Problem statement:** Học viên mất quá nhiều thời gian để xem lại video bài giảng dài hàng giờ để tìm câu trả lời cho một lỗi cụ thể, trong khi hệ thống AI Tutor hiện tại thường xuyên phản hồi "không tìm thấy thông tin" do thiếu ngữ cảnh toàn cục của Slide & Transcript, khiến lực lượng Trợ giảng bị quá tải bởi các câu hỏi bị chuyển tiếp sang.
- **Evidence:**
  - **Số liệu mining (Phân tích thực tế từ `chat_history_anonymized_for_hackathon.csv`):**
    - Mẫu phân tích gồm $2,522$ lượt hội thoại ($1,261$ câu hỏi học viên) trên $369$ học viên duy nhất và $585$ phiên hội thoại.
    - Có **$134$ câu hỏi ($10.63\%$)** trực tiếp yêu cầu AI tóm tắt bài giảng, tóm gọn slide hoặc trích xuất ý chính.
    - Trong $134$ lượt hỏi tóm tắt đó, hệ thống AI Tutor hiện tại trả lời **thất bại / báo không tìm thấy thông tin ở $49$ lượt ($36.57\%$)** do thiếu ngữ cảnh toàn cục từ Slide & Transcript.
    - Tổng cộng toàn hệ thống có **$210$ lượt ($16.65\%$)** AI trả lời thất bại (báo lỗi không có thông tin/xin lỗi).
  - **$\ge 5$ quote/ví dụ nguyên văn + nguồn (Trích xuất chính xác từ CSV):**
    1. *"(Trang 37, đoạn được chọn: 'tóm tắt nội dung chính trong slide này')\ntóm tắt nội dung chính trong slide này"* (Log ID #M1149 - User U0067)
    2. *"(Trang 50, đoạn được chọn: 'tóm gọn những nội dung quan trọng nhất trong day 04 này')\ntóm gọn những nội dung quan trọng nhất trong day 04 này"* (Log ID #M2275 - User U0031)
    3. *"(Trang 14, đoạn được chọn: 'tóm tắt các chủ đề chính của slide day05-lecture-slides-batch03.pdf này')\ntóm tắt các chủ đề chính của slide day05-lecture-slides-batch03.pdf này"* (Log ID #M2134 - User U0168)
    4. *"(Trang 70, đoạn được chọn: 'tóm tắt nội dung, đưa ra keyword cần nhớ')\ntóm tắt nội dung, đưa ra keyword cần nhớ"* (Log ID #M1830 - User U0365)
    5. *"(Trang 17, đoạn được chọn: 'tóm gọn lại về kiến trúc Agent')\ntóm gọn lại về kiến trúc Agent"* (Log ID #M0272 - User U0212)

---

## §2. Impact & quyết định chọn
- **Bảng impact $\ge 3$ ứng viên:**

| Ứng viên tính năng | Đối tượng & Số lượng | Tần suất | Tốn gì mỗi lần (Pain) | Khả thi kỹ thuật |
| :--- | :--- | :--- | :--- | :--- |
| **1. AI Tóm tắt Slide + Transcript & Trả lời tự động (RAG + HITL Gate)** | 369 Học viên + 5 TA | Hàng ngày | Học viên bị AI từ chối $36.57\%$ lượt tóm tắt; TA tốn 3–4 tiếng/ngày giải đáp thủ công. | **Cao** (Đã có Transcript `.txt` & API LLM JSON Mode) |
| **2. AI Auto-grading (Tự động chấm code bài tập)** | 369 Học viên | 1 lần/tuần | 1–2 tiếng làm sandbox chạy thử | **Trung bình** (Phụ thuộc hạ tầng Sandbox/Docker) |
| **3. AI Recommendation System (Gợi ý lộ trình học cá nhân)** | 369 Học viên | 1 lần/tháng | 10 phút xem đề xuất | **Thấp** (Thiếu dữ liệu hành vi dài hạn) |

- **Ứng viên ĐÃ LOẠI + vì sao:** 
  - *Ứng viên 2 (Auto-grading):* Chi phí hạ tầng cao, rủi ro bảo mật khi chạy code sinh viên.
  - *Ứng viên 3 (Recommendation):* Tần suất sử dụng thấp, không giải quyết đúng điểm tắc nghẽn $36.57\%$ tỷ lệ thất bại khi tóm tắt bài giảng hiện tại.
- **Ứng viên CHỌN + vì sao (bằng số):** **Ứng viên 1**. Khắc phục trực tiếp $36.57\%$ tỷ lệ AI báo lỗi không tìm thấy tài liệu khi tóm tắt, giúp tự động xử lý $10.63\%$ nhu cầu tóm tắt của $369$ học viên, giảm $70\%$ thời gian phản hồi của TA nhờ luồng duyệt bản nháp (AI Draft).

---

## §3. Giải pháp tương tự đã nghiên cứu
- **Kharagpur / Coursera AI Assistant:** 
  - *Flow:* Chatbot hỗ trợ bên cạnh video bài giảng.
  - *Đáng học:* Giao diện gắn liền với mốc thời gian (timestamp) của bài giảng.
  - *Đáng né:* Trả lời hoàn toàn tự động mà không có vòng kiểm duyệt của con người, dẫn đến nhiều câu trả lời ảo (hallucination) khiến sinh viên hiểu sai.
  - *Mình khác gì:* Tích hợp **Human-in-the-Loop (HITL) Gate với threshold $0.85$** — chỉ tự động trả lời khi chắc chắn, còn lại chuyển nháp cho TA duyệt.
- **Custom GPTs (OpenAI):** 
  - *Flow:* Upload PDF slide/transcript rồi chat trực tiếp.
  - *Đáng học:* Tốc độ phản hồi nhanh, trích xuất text tốt.
  - *Đáng né:* Không phân quyền giữa Học viên và Trợ giảng; không tự động tóm tắt đa file transcript.
  - *Mình khác gì:* Chia rõ 2 giao diện (Student UI / TA Dashboard), cho phép TA chỉnh sửa câu trả lời nháp của AI trước khi gửi.

---

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** Một học viên gửi thắc mắc hoặc yêu cầu tóm tắt bài giảng, hệ thống AI đọc 5 file Transcript/Slide để tạo câu trả lời nháp kèm điểm tự tin; nếu điểm tự tin $< 0.85$, câu hỏi được chuyển cho Trợ giảng duyệt trước khi gửi kết quả chính thức cho học viên.
- **Non-goals ($\ge 3$ thứ KHÔNG build):**
  - KHÔNG build hệ thống điểm danh tự động hay webcam proctoring.
  - KHÔNG build trình biên dịch/chạy code trực tuyến (Online Compiler/Sandbox).
  - KHÔNG tự động gửi email/SMS thông báo cho học viên.
- **Mức prototype nhắm tới:** [x] Working — phần mock: *Database lưu bằng SQLite/JSON local*; phần thật: *Toàn bộ Luồng RAG đọc Transcript/Slide, Prompt System ép JSON Mode, LLM Engine tính Confidence Score và Giao diện HITL Queue cho TA*.
- **Automation:** [x] conditional — *Lý do (cost-of-error):* Nếu AI trả lời sai kiến thức lập trình cho $369$ học viên, chi phí sửa sai rất lớn. Do đó chỉ tự động 100% khi $Confidence \ge 0.85$, nếu dưới ngưỡng bắt buộc phải qua con người (TA).
- **§4b. Nguyên tắc đã áp dụng ($\ge 4$ — HAX/PAIR):**

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
| :--- | :--- |
| **G2: Make clear how well the system can do what it can do** | Hiển thị rõ điểm `Confidence Score` và nhãn nháp `[AI Draft]` trên giao diện TA Dashboard. |
| **G9: Support efficient correction** | Cho phép Trợ giảng chỉnh sửa trực tiếp nội dung `draft_response` của AI chỉ bằng 1-click trước khi nhấn nút "Duyệt & Gửi". |
| **G11: Make clear why the system did what it did** | Trong phản hồi JSON của AI có trường `reasoning_steps` (Chain-of-Thought) giải thích lý do đưa ra câu trả lời đó. |
| **G13: Scope services based on context** | Khi độ tự tin thấp ($< 0.85$), hệ thống tự động giảm phạm vi hoạt động từ "Trả lời ngay" sang "Đã nhận câu hỏi - Đang chờ Trợ giảng kiểm duyệt". |

---

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản ($\ge 8$)

| STT | Lớp chỗ khó (Error Layer) | Kịch bản lỗi thực tế (Edge Case) | Cách hệ thống xử lý / Kịch bản dự phòng |
| :---: | :--- | :--- | :--- |
| 1 | **1. Ambiguity / Phức tạp** | Học viên hỏi quá ngắn: *"Lỗi này sửa sao?"* (Không kèm code/ảnh). | AI trả về `confidence: 0.3`, phân loại `intent: Unknown`, phản hồi nháp yêu cầu học viên cung cấp thêm chi tiết code và đẩy về TA Queue. |
| 2 | **1. Ambiguity / Phức tạp** | Câu hỏi chứa câu hỏi kép (2 ý mâu thuẫn trong 1 tin nhắn). | AI tách ý trong `reasoning_steps`, trả lời ý có thông tin trong transcript, đánh dấu điểm tin cậy $0.70$ để TA rà soát lại. |
| 3 | **2. Hallucination / Lệch tri thức** | Học viên hỏi về kiến thức nâng cao không có trong 5 bài giảng (ví dụ: *"Thầy dạy về Kubernetes chưa?"*). | Prompt khống chế AI chỉ được dùng thông tin trong Transcript. Nếu không có, gán `confidence: 0.2`, xuất câu nháp: *"Kiến thức này chưa có trong bài giảng"*. |
| 4 | **2. Hallucination / Lệch tri thức** | AI tự bịa ra hạn nộp bài tập không có trong Transcript. | Bộ kiểm tra quy tắc (Rule-check) phát hiện từ khóa "Deadline" nhưng thiếu `source_part` tương ứng $\rightarrow$ Hạ `confidence` xuống dưới $0.85$. |
| 5 | **3. Out-of-Scope / Spam** | Học viên hỏi câu hỏi cá nhân/đời tư hoặc đố vui: *"Thầy giáo bao nhiêu tuổi?"* | System Prompt nhận diện `intent: Out_Of_Scope`, phản hồi lịch sự hướng học viên quay lại nội dung bài học, không tốn tài nguyên RAG. |
| 6 | **3. Out-of-Scope / Spam** | Học viên gửi đoạn code rác / spam ký tự tự do (`asdfghjkl...`). | AI bắt lỗi định dạng, trả về câu thông báo yêu cầu nhập đúng cú pháp câu hỏi. |
| 7 | **4. System/API Failure** | API OpenAI/Gemini bị timeout hoặc hết quota token. | Code Backend catch exception, trả về thông báo: *"Hệ thống AI đang bận, câu hỏi đã được ghi nhận trực tiếp vào hàng chờ của Trợ giảng"*. |
| 8 | **4. System/API Failure** | File transcript bị lỗi mã hóa font chữ (encoding utf-8). | Module `knowledge_loader.py` có try-except fallback tự động bỏ qua đoạn lỗi và ghi log cảnh báo ra server console. |

---

## §6. Bốn đường đi của trải nghiệm
- **Happy path:** Học viên gửi câu hỏi $\rightarrow$ AI tìm thấy thông tin chính xác trong Transcript Part 2 $\rightarrow$ $Confidence = 0.92 \ge 0.85$ $\rightarrow$ Hiển thị ngay câu trả lời cho học viên với badge *"AI Verified"*.
- **Low-confidence (②):** Học viên hỏi lỗi code nâng cao $\rightarrow$ AI tạo câu trả lời nháp nhưng $Confidence = 0.65 < 0.85$ $\rightarrow$ Học viên nhận thông báo *"Đang chờ TA kiểm duyệt"* $\rightarrow$ Đẩy vào Dashboard TA $\rightarrow$ TA nhấn `[Duyệt]` $\rightarrow$ Phản hồi xuất hiện ở giao diện Học viên.
- **Failure/không căn cứ (①):** Học viên hỏi kiến thức ngoài khóa học $\rightarrow$ AI không tìm thấy tài liệu căn cứ ($Confidence = 0.10$) $\rightarrow$ Trả về thông báo: *"Nội dung này nằm ngoài phạm vi 5 bài giảng. Đã chuyển cho TA hỗ trợ riêng"*.
- **Correction (user sửa):** Trợ giảng đọc câu nháp của AI trên Dashboard thấy giải thích chưa sát $\rightarrow$ TA bấm `[Sửa nháp]`, bổ sung thêm 1 dòng lưu ý $\rightarrow$ Bấm `[Gửi]` $\rightarrow$ Hệ thống lưu phiên bản sửa của TA để finetune prompt sau này.
- **Khi bị đòi ngoài phạm vi (③):** Học viên hỏi: *"Viết hộ em bài luận môn Triết học"* $\rightarrow$ AI nhận diện `intent: Out_Of_Scope` $\rightarrow$ Từ chối ngắn gọn: *"Tôi chỉ hỗ trợ giải đáp kiến thức trong khóa học Lập trình & AI này"*.
- **Case đặc thù domain (④):** Học viên gửi tin nhắn chứa đoạn code bị lỗi Syntax $\rightarrow$ AI nhận diện `intent: Technical_Bug` $\rightarrow$ Kích hoạt chuỗi suy luận Chain-of-Thought (CoT) để chỉ ra đúng dòng code bị lỗi và đưa ra đoạn code đã sửa mẫu.

---

## §7. Kiểm thử
- **Chiều chất lượng + định nghĩa kiểm chứng được:**
  1. *JSON Validity Rate:* $100\%$ response từ LLM API phải parse thành công thành `json_object` hợp lệ theo schema.
  2. *Precision of Gate (HITL):* $0\%$ câu trả lời sai kiến thức nghiêm trọng được tự động gửi ($Confidence \ge 0.85$).
  3. *Latency:* Thời gian phản hồi API RAG $< 3.5$ giây.
- **Golden set ($\ge 20$ case theo cơ cấu):**
  - 8 câu hỏi có sẵn đáp án rõ ràng trong Transcript (Test Happy path).
  - 5 câu hỏi mập mờ/lỗi code phức tạp (Test Low-confidence path).
  - 4 câu hỏi nằm ngoài nội dung 5 bài giảng (Test Out-of-Scope).
  - 3 câu hỏi tóm tắt Slide/bài học (Test Summarization).
  *(Chi tiết danh sách 20 case lưu tại file `backend/app/data/eval/golden_set.json`)*.
- **Quality bar (chốt từ 23:59, giữ nguyên sau đó):** "Đạt khi $\ge 85\%$ vượt qua bộ Golden Set, và $100\%$ output tuân thủ đúng định dạng JSON Schema."
- **Kết quả các lượt chạy:**

| Lượt chạy (Run) | Ngày chạy | Số case đạt / Tổng | % Đạt | Ghi chú điều chỉnh |
| :---: | :---: | :---: | :---: | :--- |
| Run 1 (Baseline) | 28/07/2026 | 13/20 | $65.0\%$ | Chưa áp dụng CoT trong System Prompt, sai format JSON ở 3 case. |
| Run 2 (Prompt v2) | 30/07/2026 | 16/20 | $80.0\%$ | Đã thêm `response_format={"type": "json_object"}` và chi tiết hóa thang điểm Confidence. |
| Run 3 (Final CP4) | 31/07/2026 | 18/20 | **$90.0\%$** | Đạt Quality Bar. Tích hợp trọn vẹn 5 file transcript và parser slide. |

---

## §8. Phân công & kế hoạch
- **Phân công có tên:**
  - `Trần Văn A` — Spec, Evidence Mining & Viết báo cáo.
  - `Lê Thị B` — Prompt Engineering (`prompts.py`) & Golden Set Evaluation.
  - `Nguyễn Văn C` — Backend Architecture (`llm_engine.py`, `student_router.py`, `ta_router.py`).
  - `Phạm Văn D` — Frontend Development (Student UI & TA Dashboard).
- **Willing users ($\ge 3$ tên) + kế hoạch vòng validation CP5:**
  - *3 Willing users:* Trợ giảng Hoàng (TA chính), Học viên Minh (Lớp Python), Học viên Linh (Lớp AI).
  - *Kế hoạch CP5:* Cho 3 user thao tác trực tiếp trên bản Demo Working trong 30 phút. Log lại 3 câu hỏi:
    1. *Hệ thống có giúp tiết kiệm thời gian tìm kiếm/trả lời không?*
    2. *Bản tóm tắt slide và câu trả lời nháp của AI có chính xác không?*
    3. *Thao tác duyệt bài trên TA Dashboard có thuận tiện không?*
- **Multi-prototype (nếu làm):**
  - *Phương án A (Direct RAG):* Đưa toàn bộ 5 transcript vào Prompt mỗi lần gọi.
  - *Phương án B (Vector Search / Embeddings RAG):* Đăng ký Vector DB (ChromaDB) để retrieve đoạn văn bản liên quan.
  - *Lựa chọn:* Chọn **Phương án A** cho phạm vi bài giảng nhỏ (5 file transcript) để giảm thiểu độ phức tạp hạ tầng và đảm bảo tốc độ phản hồi demo ổn định.

---

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
| :---: | :--- | :--- |
| **28/07/2026** | Khởi tạo file `spec.md` ban đầu | Thống nhất cấu trúc Clean Architecture & Luồng RAG + HITL. |
| **30/07/2026** | Bổ sung phần tóm tắt Slide (`slide_parser.py`) vào §4 | Dựa trên phản hồi người dùng về việc Slide quá ít chữ, cần kết hợp Transcript để tóm tắt sâu. |
| **31/07/2026** | Cập nhật số liệu mining chuẩn từ dataset `chat_history_anonymized_for_hackathon.csv` (§1 & §2) | Đảm bảo tính chính xác tuyệt đối của bằng chứng dữ liệu trước khi nộp Checkpoint 4. |