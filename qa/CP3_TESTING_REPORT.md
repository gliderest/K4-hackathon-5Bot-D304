# Báo cáo Testing — CP3

## 1. Mục tiêu kiểm thử

Xác minh tutor có thể trả lời câu hỏi dựa trên slide/transcript, giữ citation, xử lý input mơ hồ và từ chối yêu cầu ngoài phạm vi.

## 2. Phạm vi hệ thống

- Backend FastAPI của VLearn Cross-Lesson AI Tutor.
- Retrieval local từ transcript và slide trong data pack.
- AI call thật qua OpenRouter.
- Frontend React được kiểm tra bằng production build.
- Long-term progress được kiểm tra qua API.

## 3. Bộ kiểm thử

Golden Set gồm **21 case**, bao phủ:

- Happy path.
- Source truth / grounding.
- Input mơ hồ hoặc thiếu context.
- Yêu cầu ngoài phạm vi.
- Lỗi đặc thù domain.
- Edge case như input rỗng hoặc chỉ có ký tự đặc biệt.

## 4. Quality Bar

- Overall pass rate tối thiểu: **80%**.
- Critical hallucination: **0**.
- Case yêu cầu citation phải có citation.

## 5. Kết quả CP3

| Chỉ số | Kết quả |
|---|---:|
| Tổng số case | 21 |
| Case pass | 21 |
| Case fail | 0 |
| Pass rate | **100%** |
| Critical failure | **0** |
| AI call | OpenRouter, `openai/gpt-4o-mini` |
| Chế độ chạy | HTTP end-to-end |

Run chính thức:

- Run ID: `run-456be9f22a51`
- Summary: `qa/eval/reports/run-456be9f22a51_summary.md`
- Raw results: `qa/eval/runs/run-456be9f22a51.json`

## 6. Các hành vi đã xác minh

### Câu hỏi có nguồn

Tutor truy xuất transcript/slide, gọi AI thật và trả lời kèm citation tương ứng.

### Câu hỏi mơ hồ

Tutor không đoán. Hệ thống yêu cầu người học làm rõ lesson, chủ đề hoặc đoạn tài liệu cần hỏi.

### Input rỗng hoặc không có nghĩa

Hệ thống trả về clarification thay vì lỗi API `422` hoặc câu trả lời bịa.

### Yêu cầu ngoài phạm vi

Các yêu cầu như lấy điểm cuối kỳ, tư vấn y tế hoặc làm hộ bài kiểm tra bị từ chối và chuyển hướng sang hỗ trợ ôn tập.

### Citation

Citation được tạo từ kết quả retrieval và được backend bảo toàn; model không được tự tạo citation không tồn tại.

## 7. Kiểm thử bổ sung

- Backend tests: **4 passed**.
- QA tests: **10 passed**.
- Frontend TypeScript/Vite build: **pass**.
- Health API: **200 OK**.
- Course outline, lesson detail, chat và progress API: **pass**.

## 8. Câu trả lời ngắn khi được hỏi tại CP3

### Vì sao dùng Golden Set?

Golden Set cố định các tình huống quan trọng và rủi ro để mỗi phiên bản đều được kiểm tra cùng một chuẩn, thay vì chỉ đánh giá bằng cảm nhận.

### Vì sao cần test case lỗi?

Tutor không chỉ cần trả lời đúng khi có đủ dữ liệu. Nó còn phải biết hỏi lại khi thiếu context, từ chối ngoài phạm vi và không bịa citation.

### AI call thật nằm ở đâu?

Sau khi retrieval tìm được các đoạn context phù hợp, Tutor Agent gửi câu hỏi và context sang OpenRouter để tạo câu trả lời. Citation vẫn do backend kiểm soát.

### Nếu API AI lỗi thì sao?

Hệ thống không tự bịa câu trả lời. Nó trả thông báo giới hạn, đặt confidence thấp và hướng dẫn người học thử lại.

### Kết luận CP3

Prototype đã có AI call thật, Golden Set 21 case và lượt evaluation end-to-end đạt **100% pass rate**, **0 critical failure**. Nhóm đủ bằng chứng kiểm thử để báo cáo CP3.

## 9. Lưu ý cho các checkpoint sau

CP3 chưa thay thế cho user validation. Ở CP5 vẫn cần test với người dùng thật, ghi observation, quote nguyên văn, feedback và changelog.
