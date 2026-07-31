# Data dùng cho hệ thống

## Nguồn chính thức

RAG mặc định chỉ index:

- `vlearn-pack/slides/*.pdf`
- `vlearn-pack/transcript/*.md`

Chatlog không phải nguồn sự thật để trả lời kiến thức, nên không đưa vào course index. Nếu dùng chatlog để tìm pain/golden set, xử lý ở luồng đánh giá riêng.

## Thư mục sinh ra

- `processed/chunks/`: JSONL sau khi tách slide và transcript.
- `vector_store/`: embedding/index của course.
- `user_uploads/{learner_id}/`: file và index riêng của từng học viên.
- `schemas/chunk.schema.json`: metadata bắt buộc để citation điều hướng đúng.

Các thư mục trên và `vlearn-pack/` đã được ignore. Không commit data pack, file upload hay vector store.

## Mapping bài học

Sao chép `catalog.example.json` thành file catalog local và cập nhật mapping giữa Day/Lesson, PDF và transcript. `lesson_id` trong catalog phải trùng với metadata của chunk và URL frontend.

