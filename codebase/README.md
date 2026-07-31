# VLearn Cross-Lesson AI Tutor

Demo full-stack local-first cho chatbot hỗ trợ học viên hỏi kiến thức trên toàn khóa học, tìm đúng slide/transcript, mở lại đúng vị trí nguồn và ghi nhớ tiến độ học tập dài hạn.

Phiên bản hiện tại đã chạy được với dữ liệu local `slides + transcript + upload`. Phần LLM provider thật vẫn để mở rộng thêm qua biến môi trường nếu đội muốn nối model ngoài sau.

## Tính năng mục tiêu

- Hỏi đáp trên toàn bộ slide và transcript của khóa học bằng RAG.
- Mỗi câu trả lời có citation chứa Day/Lesson, trang slide hoặc mã đoạn transcript.
- Click citation để điều hướng vùng nội dung ở giữa tới đúng trang/đoạn.
- Giao diện ba vùng: mục lục bên trái, slide/transcript ở giữa, chat bên phải.
- Upload PDF/DOCX/TXT trong khung chat; dữ liệu upload được index riêng theo học viên.
- Long-term memory lưu bài đã xem, tiến độ, chủ đề yếu, lịch sử ôn và gợi ý tiếp theo.
- Agent có các tool: tìm học liệu, tạo link nguồn, đọc/lưu tiến độ và tìm trong tài liệu upload.
- Khi không có căn cứ hoặc điểm tin cậy thấp, AI nói rõ giới hạn và hỏi lại; không bịa nguồn.

## Kiến trúc thư mục

```text
codebase/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # chat, course, upload, progress
│   │   ├── agent/tools/      # tools mà tutor agent được phép gọi
│   │   ├── core/             # cấu hình
│   │   ├── memory/           # long-term learning memory
│   │   ├── rag/              # ingestion, retrieval, citation
│   │   ├── schemas/          # request/response contract
│   │   └── services/         # nghiệp vụ
│   └── tests/
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/       # ba vùng giao diện + citation
│       ├── services/         # gọi FastAPI
│       └── types/
├── prompts/                  # system prompt
├── tools/                    # script ingest/index/kiểm citation
├── data/
│   ├── vlearn-pack/          # data local được cấp, không commit
│   ├── processed/            # chunks sinh ra, không commit
│   ├── vector_store/         # vector index, không commit
│   ├── user_uploads/         # file/index riêng của user, không commit
│   └── schemas/
├── storage/                  # SQLite long-term memory, không commit
├── requirements.txt
└── .env.example
```

## Workflow hệ thống

### 1. Chuẩn bị RAG

```text
slides PDF + transcript Markdown
        ↓
tools/ingest_course.py
        ↓
chunk nội dung + metadata nguồn
        ↓
embedding
        ↓
data/vector_store
```

Mỗi chunk phải giữ metadata:

- `course_id`, `day`, `lesson_id`, `title`
- `source_type`: `slide` hoặc `transcript`
- `source_file`
- `page` với slide hoặc `segment_id` với transcript
- `viewer_path` dùng để frontend mở đúng nguồn

### 2. Hỏi đáp

```text
Câu hỏi + learner_id
   ↓
Tutor agent đọc memory liên quan
   ↓
course_search / upload_search
   ↓
LLM trả lời chỉ từ context
   ↓
response + citations + suggested_next_action
   ↓
frontend render citation có thể click
```

Nếu retrieval thấp hơn `RAG_MIN_SCORE`, agent không được tự suy diễn. Nó phải hỏi lại hoặc thông báo chưa tìm thấy căn cứ.

### 3. Điều hướng citation

Backend trả citation theo contract:

```json
{
  "label": "Day 2 · Slide 8",
  "source_type": "slide",
  "lesson_id": "day-02",
  "page": 8,
  "segment_id": null,
  "viewer_path": "/learn/day-02?tab=slide&page=8"
}
```

Với transcript:

```json
{
  "label": "Day 2 · Đoạn D2-S014",
  "source_type": "transcript",
  "lesson_id": "day-02",
  "page": null,
  "segment_id": "D2-S014",
  "viewer_path": "/learn/day-02?tab=transcript&segment=D2-S014"
}
```

Khi người học click, frontend cập nhật vùng giữa và cuộn tới trang/đoạn tương ứng; không mở một trang chatbot khác.

### 4. Long-term learning memory

Chỉ lưu dữ liệu phục vụ học tập:

- bài/slide đã xem và thời điểm gần nhất;
- phần trăm hoàn thành theo lesson;
- chủ đề người học tự đánh dấu yếu;
- câu hỏi còn vướng và nội dung cần ôn lại;
- bản tóm tắt ngắn của phiên học, không mặc định lưu toàn bộ hội thoại.

Memory phải tách theo `learner_id` giả danh. Tài liệu upload và vector index của một học viên không được xuất hiện trong kết quả của người khác.

## Giao diện ba vùng

| Vùng | Chức năng |
|---|---|
| Trái | Mục lục Day/Lesson, trạng thái hoàn thành, chủ đề cần ôn |
| Giữa | PDF slide hoặc transcript; nhận lệnh điều hướng từ citation |
| Phải | Chat AI, danh sách nguồn, gợi ý ôn tiếp, nút upload tài liệu |

Màn hình nhỏ có thể chuyển thành tab hoặc drawer nhưng phải giữ cùng state bài học hiện tại.

## API dự kiến

| Method | Endpoint | Mục đích |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/courses/{course_id}/outline` | Mục lục và tiến độ |
| `GET` | `/api/sources/{source_id}` | Metadata/URL nguồn |
| `POST` | `/api/chat` | Hỏi tutor và nhận citations |
| `POST` | `/api/uploads` | Upload và index tài liệu của học viên |
| `GET` | `/api/progress/{learner_id}` | Đọc long-term progress |
| `PATCH` | `/api/progress/{learner_id}` | Cập nhật tiến độ |

Chi tiết schema nằm trong `backend/app/schemas/`.

## Chạy ở giai đoạn triển khai tiếp theo

### Backend

```powershell
cd codebase
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn backend.app.main:app --reload
```

### Frontend

```powershell
cd codebase/frontend
npm install
npm run dev
```

### Tạo index

```powershell
cd codebase
python tools/ingest_course.py
python tools/build_index.py
python tools/verify_citations.py
```

## Phần thật và phần mock cần khai báo khi demo

- AI call ở quyết định trả lời trung tâm: **phải chạy thật**.
- Retrieval từ slide/transcript: nên chạy thật; nếu mới mock phải ghi rõ.
- Long-term memory: có thể dùng SQLite local.
- Authentication và cloud storage có thể mock trong prototype.
- Không commit `.env`, API key, `data/vlearn-pack`, vector index, file upload hoặc database local.
