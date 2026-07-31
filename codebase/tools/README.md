# Tooling

- `ingest_course.py`: đọc slide/transcript và sinh chunks giữ metadata nguồn.
- `build_index.py`: tạo embedding và vector index.
- `verify_citations.py`: kiểm mọi chunk có page/segment hợp lệ và tạo được `viewer_path`.

Các script hiện là entrypoint khung. Model triển khai tiếp sẽ nối chúng với `backend/app/rag/`.

