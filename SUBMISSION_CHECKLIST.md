# Submission checklist — VLearn Cross-Lesson AI Tutor

## Hồ sơ chính

- [x] `README.md` có mô tả, thành viên, trạng thái, evidence và lệnh chạy.
- [x] `spec.md` có JTBD, problem, impact, non-goals, thiết kế, risk cases, quality bar và changelog.
- [x] Pitch deck hoàn thành trên Canva: https://slidecp1vlearn.my.canva.site/vlearn-copilot-pitch-deck
- [x] `demo-slides.md` chứa bản nội dung dự phòng/offline của pitch deck.

## Prototype và QA

- [x] Backend tests pass: 8/8.
- [x] QA tests pass: 10/10.
- [x] Golden Set validator pass: 31 cases hợp lệ.
- [x] Frontend production build pass.
- [x] Local health, outline và lesson API đã kiểm tra thành công.
- [x] System prompt có grounding, citation, clarification và scope rules.

## Evidence cần kiểm tra lần cuối

- [ ] Nếu dùng user validation làm evidence chấm điểm: điền consent, observation và quote thật trong `qa/validation/`.
- [ ] Nếu rubric yêu cầu official evaluation đúng Golden Set hiện hành: chạy lại 31 case và lưu report mới.
- [x] Feedback sơ bộ của 3 core members đã được ghi trong spec: core ổn, cần rà UI/UX.

## Vệ sinh file trước khi nộp

- [ ] Không đưa `.env` hoặc API key vào archive.
- [ ] Không đưa database local, vector index lớn, upload riêng hoặc `__pycache__` vào archive.
- [ ] Kiểm tra `git diff --check`.
- [ ] Kiểm tra archive mở được README, spec, QA và source code.
- [ ] Không để file tên `demo-slides.pdf` placeholder gây hiểu nhầm nếu submission đã dùng link Canva/PDF riêng.

## Lệnh verification cuối

```bash
cd codebase
python -m pytest -q backend/tests
python -m pytest -q ../qa/tests
python ../qa/scripts/validate_golden_set.py
cd frontend
npm run build
```
