"""Generate a fluent answer from content belonging to one currently open document."""

import asyncio

from openai import OpenAI

from backend.app.core.config import Settings
from backend.app.rag.contracts import SearchHit


CURRENT_DOCUMENT_SYSTEM_PROMPT = """Bạn là VLearn AI Tutor.
Hãy trả lời câu hỏi của học viên chỉ dựa trên phần nội dung tài liệu được cung cấp.

Nếu học viên yêu cầu tóm tắt, hãy viết một đoạn mở đầu ngắn rồi 4–7 ý chính có liên kết logic.
Nếu học viên yêu cầu giải thích hoặc phân tích, hãy giải thích mạch lạc theo thứ tự: ý chính, cách hiểu đơn giản, ví dụ chỉ khi ví dụ có trong tài liệu.
Nếu học viên yêu cầu tạo quiz, câu trắc nghiệm, flashcard hoặc bài tập, hãy tạo đúng số lượng mà họ yêu cầu từ tài liệu đang mở. Với trắc nghiệm, mỗi câu có 4 lựa chọn A–D, chỉ một đáp án đúng; đặt đáp án và giải thích ngắn sau toàn bộ danh sách câu hỏi.
Không liệt kê đoạn trích thô, không nói về quá trình tìm kiếm, không nhắc “citation”, không đưa link hoặc nguồn.
Không bịa thêm kiến thức ngoài tài liệu. Nếu nội dung cung cấp chưa đủ để trả lời, nói ngắn gọn phần nào chưa có trong tài liệu.
Trả lời bằng tiếng Việt tự nhiên, trực tiếp và có cấu trúc Markdown dễ đọc."""


class CurrentDocumentWriter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        provider = settings.ai_provider.lower()
        self.enabled = (
            provider in {"openai", "openrouter"}
            and bool(settings.ai_api_key)
            and bool(settings.ai_model)
        )
        self.provider = provider
        self._client = self._build_client() if self.enabled else None

    def _build_client(self) -> OpenAI:
        kwargs: dict[str, str] = {"api_key": self.settings.ai_api_key}
        if self.settings.ai_base_url:
            kwargs["base_url"] = self.settings.ai_base_url
        elif self.provider == "openrouter":
            kwargs["base_url"] = "https://openrouter.ai/api/v1"
        return OpenAI(**kwargs)

    async def write(
        self,
        question: str,
        document_title: str,
        hits: list[SearchHit],
    ) -> str | None:
        if not self.enabled or self._client is None:
            return None
        context = self._build_context(hits)
        if not context:
            return None
        try:
            return await asyncio.to_thread(
                self._write_sync,
                question,
                document_title,
                context,
            )
        except Exception:
            # A local fallback remains available if the provider is temporarily unavailable.
            return None

    def _write_sync(self, question: str, document_title: str, context: str) -> str | None:
        assert self._client is not None
        response = self._client.chat.completions.create(
            model=self.settings.ai_model,
            temperature=0.2,
            max_tokens=900,
            messages=[
                {"role": "system", "content": CURRENT_DOCUMENT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"TÀI LIỆU ĐANG MỞ: {document_title}\n\n"
                        f"CÂU HỎI: {question}\n\n"
                        f"NỘI DUNG TÀI LIỆU:\n{context}"
                    ),
                },
            ],
        )
        content = response.choices[0].message.content
        return content.strip() if content else None

    @staticmethod
    def _build_context(hits: list[SearchHit]) -> str:
        sections = []
        for index, hit in enumerate(hits, start=1):
            text = hit.chunk.text.strip()
            if not text:
                continue
            sections.append(f"[Phần {index}]\n{text[:2600]}")
        return "\n\n---\n\n".join(sections)[:26000]
