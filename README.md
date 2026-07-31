# VLearn Cross-Lesson AI Tutor — 5Bot-D304

## Thông tin thành viên

- T012 — Nguyễn Trọng Toàn — Core/Product & Spec
- T012 — Sái Hồng Anh — Core/Product & UX review
- T015 — Nguyễn Hoàng Anh — Core/Product & Prototype/Demo

## Phân công việc

- **Spec & Evidence**: Nguyễn Trọng Toàn
- **Prompt Engineering**: Nhóm core phối hợp
- **Code/Prototype**: Nguyễn Hoàng Anh và nhóm core
- **Demo Preparation**: Nhóm core phối hợp
- **Validation & User Testing**: Sái Hồng Anh điều phối, cả nhóm tham gia

## Mô tả ngắn gọn về dự án

VLearn Cross-Lesson AI Tutor giúp học viên hỏi đáp trên slide/transcript của khóa học, nhận câu trả lời có citation, mở đúng vị trí nguồn, upload tài liệu cá nhân và theo dõi tiến độ học tập. Khi không có căn cứ, tutor hỏi lại hoặc từ chối thay vì bịa.

## Trạng thái hiện tại

- Spec: Đã hoàn thành bản working draft — xem `spec.md`
- Prototype: Working local prototype — xem `codebase/README.md`
- Demo slides: Đã hoàn thành — pitch deck Canva ở phần Pitch deck
- Validation: Đã có feedback sơ bộ; cần hoàn tất observation/consent/quote trong `qa/validation/`

## Bằng chứng và kiểm tra

- Spec: `spec.md`
- Backend tests: `codebase/backend/tests/`
- QA tests và Golden Set: `qa/tests/`, `qa/eval/`
- Validation: `qa/validation/`
- System prompt: `codebase/prompts/system-prompt.md`
- Hướng dẫn chạy: `codebase/guide_run.md`

Từ thư mục `codebase` chạy:

```bash
python -m pytest -q backend/tests
python -m pytest -q ../qa/tests
python ../qa/scripts/validate_golden_set.py
cd frontend && npm run build
```

Không commit `.env`, API key, database, vector index, upload riêng hoặc cache.

## Pitch deck

Pitch deck Canva: https://slidecp1vlearn.my.canva.site/vlearn-copilot-pitch-deck

Khi nộp bản archive, nên tải thêm PDF từ Canva vào repo hoặc submission portal nếu yêu cầu file offline.

_Lưu ý: Repo này sẽ được nộp cuối cùng trước CP6 (12:00 ngày 2). Spec phải được nộp đúng hạn vào 23:59 ngày 1 để được tính điểm checkpoint._
