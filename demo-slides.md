# VLearn Cross-Lesson AI Tutor — Demo deck

## Slide 1 — Problem

Học viên phải tìm câu trả lời giữa nhiều slide/transcript, khó kiểm tra nguồn và dễ quên phần cần ôn. Tutor cần hữu ích nhưng không được bịa khi không có căn cứ.

## Slide 2 — User & JTBD

Khi đang học một lesson và gặp câu hỏi, học viên muốn nhận giải thích ngắn, có căn cứ và mở được đúng vị trí nguồn để tiếp tục học.

## Slide 3 — Solution

Một màn hình ba vùng:

- Trái: Day/Lesson và tiến độ.
- Giữa: slide/transcript đang học.
- Phải: chat tutor, citation và gợi ý ôn.

## Slide 4 — Core demo flow

1. Chọn lesson.
2. Hỏi tutor.
3. Tutor truy xuất context.
4. Trả lời kèm citation.
5. Click citation để mở đúng slide/đoạn transcript.
6. Hỏi tiếp hoặc lưu tiến độ.

## Slide 5 — Trust & safety

- Citation do backend kiểm soát.
- Confidence thấp thì hỏi lại.
- Không có nguồn thì không suy diễn.
- Từ chối làm hộ bài kiểm tra, cho điểm hoặc tư vấn ngoài phạm vi.

## Slide 6 — Implementation

FastAPI + React/Vite + RAG local + AI provider thật qua cấu hình + SQLite learning memory. Upload document được tách theo learner ID.

## Slide 7 — QA evidence

- Backend tests: 8/8 pass.
- QA tests: 10/10 pass.
- Golden Set: 31 cases hợp lệ.
- Official run lịch sử: 21/21, 0 critical fail.
- Cần chạy lại official run trên 31 case trước khi nộp.

## Slide 8 — User feedback

Feedback sơ bộ của T012 Nguyễn Trọng Toàn, T012 Sái Hồng Anh và T015 Nguyễn Hoàng Anh: core flow ổn; cần rà soát UI và trải nghiệm người dùng.

Không đưa phần trăm hoặc quote nguyên văn vào slide cho đến khi đã ghi consent và observation thật trong `qa/validation/`.

## Slide 9 — Next iteration

- Làm nổi bật citation và trạng thái low-confidence.
- Giảm hesitation khi chọn tài liệu.
- Kiểm tra responsive layout.
- Chạy usability test và cập nhật theo evidence.
