# Mini Hackathon AI Project Repository — AI Tutor for vlearn.dev

## 👥 Thông tin thành viên & Phân công công việc

| Mã sinh viên | Họ và tên | Trách nhiệm chính | Phân công chi tiết |
| :--- | :--- | :--- | :--- |
| **2A202601850** | Nguyễn Tiến Đạt | **Spec & Evidence** | Xây dựng tài liệu `spec.md`, khai phá dữ liệu mining ($134$ hội thoại), thu thập bằng chứng lỗi, code frontend |
| **2A202601614** | Tống Tiến Mạnh | **Prompt Engineering** | Thiết kế Prompt RAG, tối ưu hóa output JSON (`reasoning_steps`) & logic tính `Confidence Score` |
| **2A202601126** | Bùi Thái Sơn | **Code/Prototype** | Phát triển luồng RAG, tích hợp HITL Gate (ngưỡng $0.85$) & xây dựng giao diện TA Dashboard |
| **2A202601526** | Nguyễn Công Đạt | **Demo Preparation** | Lập kịch bản demo (3–5 phút), chuẩn bị dữ liệu mẫu và slide thuyết trình CP5/CP6 |
| **2A202601580** | Nguyễn Văn Thắng | **Validation & User Testing** | Xây dựng bộ Golden Set ($20$ test cases), kiểm thử giao diện TA Dashboard và thu thập phản hồi người dùng |

---

## 📝 Mô tả ngắn gọn về dự án

**AI Tutor for vlearn.dev** là giải pháp trợ lý học tập thông minh áp dụng mô hình **RAG (Retrieval-Augmented Generation)** kết hợp cơ chế kiểm duyệt **HITL (Human-in-the-Loop Gate)**. 

Dựa trên phân tích thực tế từ $134$ lượt hỏi tóm tắt bài học, nhóm phát hiện có **$49$ lượt ($36.57\%$) AI tự trả lời thất bại** do câu hỏi mập mờ hoặc thiếu ngữ cảnh. Hệ thống mới được thiết kế với cơ chế tự đánh giá độ tự tin (`Confidence Score`):
* **Nếu điểm tự tin $\ge 0.85$:** AI tự động trả lời học viên tức thì dựa trên Slide & Transcript của bài học.
* **Nếu điểm tự tin $< 0.85$:** Hệ thống tự động thu hẹp phạm vi, chuyển câu hỏi về hàng chờ **TA Dashboard** để Trợ giảng chỉnh sửa 1-click và duyệt bài trước khi gửi cho học viên.

Giải pháp đảm bảo tính **minh bạch (HAX/PAIR G2, G9, G11, G13)**, giúp giảm $60-70\%$ tải công việc cho Trợ giảng mà vẫn đảm bảo học viên nhận được thông tin chuẩn xác $100\%$.

---

## 📌 Trạng thái hiện tại

* **Spec:** Đã hoàn thành (File `spec.md` đã sẵn sàng cho Checkpoint)
* **Prototype:** Working (Đã chạy được luồng RAG, HITL Gate & TA Dashboard)
* **Demo slides:** Đang làm (Đang hoàn thiện slide 3-5 phút phục vụ CP5)
* **Validation:** Đang thực hiện (Đang chạy kiểm thử trên Golden Set 20 cases & phỏng vấn user)

> **Lưu ý:** Repo này sẽ được nộp cuối cùng trước CP6 (12:00 ngày 2). Spec được nộp đúng hạn trước 23:59 ngày 1 để ghi nhận điểm checkpoint.