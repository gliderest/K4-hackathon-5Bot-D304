# QA Testing & User Validation

Module độc lập này phục vụ Golden Set, evaluation, regression và user validation cho VLearn tutor. Nó không import hoặc sửa prototype HTML. Trước khi Dev hoàn thành API, nhóm có thể validate dataset, chạy unit test, hoàn thiện rubric và chuẩn bị phiên user test. Chỉ chạy evaluation chính thức sau khi có API thật.

## Cài đặt và cấu hình

Từ thư mục gốc: `python -m pip install -r qa/requirements.txt`. Sao chép `qa/config/.env.example` thành file môi trường bên ngoài repo; đặt `AI_API_URL`, method, timeout, key và model/version nếu có. Không commit secret.

## Lệnh

- `python qa/scripts/validate_golden_set.py`
- `pytest -q qa/tests`
- `python qa/scripts/run_eval.py --mode mock` (chỉ kiểm tra module; `official=false`)
- `python qa/scripts/run_eval.py --mode http` (chỉ khi API đã cấu hình)
- `python qa/scripts/generate_report.py --run-id <run_id>`
- `python qa/scripts/compare_runs.py --baseline <id> --candidate <id>`

Thêm case bằng cách thêm một dòng CSV, giữ `case_id` duy nhất, đúng bốn risk class và ghi `source_reference`. Chỉ dùng `source=chatlog` khi tìm thấy câu thật trong repository. Các case hiện tại đều là `sample`.

## Chấm và báo cáo

Rule-based checks bao phủ output rỗng, citation hiện diện, refusal và clarification pattern. Groundedness, citation correctness, answer correctness và domain quality cần reviewer; không dùng LLM-as-a-judge làm quyết định duy nhất. Mỗi run được lưu riêng trong `qa/eval/runs/`, không ghi đè. Summary dùng cho Slide 4; validation summary dùng cho Slide 5 và `spec.md` §7–§9.

## User validation

Điền participants sau khi có consent thật, chạy script 5–10 phút, ghi hành vi và quote nguyên văn trong observation sheet, sau đó tổng hợp feedback. Không tự tạo tên, quote hoặc tỷ lệ.

## Giải thích trong demo

“Đây là lớp QA độc lập đứng giữa prototype và quyết định demo: Golden Set cố định các tình huống rủi ro, runner lưu từng lần chạy, rubric tách lỗi critical khỏi review thủ công, còn regression report cho biết phiên bản mới có làm xấu đi case nào không. User validation bổ sung bằng chứng người dùng thật; mọi số liệu đều truy về run hoặc biểu mẫu, không fake.”
