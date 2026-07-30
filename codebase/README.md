# VLearn AI Tutor — Prototype

Prototype minh hoạ AI Tutor hỗ trợ học viên tìm và ôn kiến thức xuyên suốt khóa học.

## Cấu trúc

- `src/`: mã nguồn giao diện và logic chatbot.
- `public/`: ảnh và tài nguyên giao diện tĩnh.
- `prompts/system-prompt.md`: quy tắc và prompt hệ thống cho AI.
- `data/demo-data.json`: dữ liệu giả dùng trong demo.

## Phần thật và phần mock

| Hạng mục | Trạng thái |
|---|---|
| Giao diện chatbot | Sẽ build trong `src/` |
| Tìm kiếm học liệu | Có thể mock bằng `data/demo-data.json` hoặc kết nối data local |
| Câu trả lời AI | Phải có ít nhất một lời gọi AI thật ở quyết định trung tâm |
| Nguồn trích dẫn | Hiển thị từ metadata của tài liệu tìm được |

## Cấu hình an toàn

1. Sao chép `.env.example` thành `.env` trên máy local.
2. Điền API key vào `.env`.
3. Không commit `.env`, API key hoặc data pack gốc.

> Lệnh chạy sẽ được bổ sung sau khi nhóm chọn stack (ví dụ React/Vite hoặc Next.js).
