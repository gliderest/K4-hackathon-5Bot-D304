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

ANSWER_SYSTEM_PROMPT = """Bạn là VLearn AI Tutor của khóa học AI Thực Chiến.
Trả lời câu hỏi bằng tiếng Việt, trực tiếp và dễ hiểu, chỉ dựa trên CONTEXT được cung cấp.
Không nhắc đến quá trình tìm kiếm, không liệt kê các đoạn trích thô và không bịa thông tin.
Nếu context không đủ để kết luận, nói rõ phần chưa đủ căn cứ và hỏi người học một câu làm rõ.
Ưu tiên trả lời đúng ý định của câu hỏi. Với câu chào, xã giao hoặc câu hỏi đơn giản,
chỉ trả lời 1–3 câu ngắn. Chỉ giải thích dài khi người học yêu cầu chi tiết.
Giữ câu trả lời dưới 120 từ nếu người học không yêu cầu giải thích sâu."""

COMPARE_SYSTEM_PROMPT = """Bạn là VLearn AI Tutor. Hãy đối chiếu TÀI LIỆU NGƯỜI HỌC với KIẾN THỨC KHÓA HỌC.
Chỉ dùng nội dung được cung cấp, không bịa và không đánh đồng thiếu thông tin với sai.
Trả lời bằng tiếng Việt, Markdown ngắn gọn theo 4 mục:
1. Điểm giống
2. Điểm khác hoặc chưa đủ căn cứ
3. Phần áp dụng đúng/chưa đúng
4. Đề xuất cải thiện
Mỗi nhận xét phải dựa trên một hoặc cả hai nguồn. Không tự tạo citation hoặc tên nguồn."""


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

    async def write_answer(self, question: str, hits: list[SearchHit]) -> str | None:
        """Generate a grounded answer for questions spanning the course corpus."""
        if not self.enabled or self._client is None:
            return None
        context = self.build_answer_context(hits)
        if not context:
            return None
        try:
            return await asyncio.to_thread(self._write_answer_sync, question, context)
        except Exception:
            return None

    async def write_comparison(
        self,
        question: str,
        document_title: str,
        document_hits: list[SearchHit],
        course_hits: list[SearchHit],
    ) -> str | None:
        if not self.enabled or self._client is None:
            return None
        document_context = self.build_answer_context(document_hits, minimum_score=0.0)
        course_context = self.build_answer_context(course_hits, minimum_score=0.45)
        if not document_context or not course_context:
            return None
        try:
            return await asyncio.to_thread(
                self._write_comparison_sync,
                question,
                document_title,
                document_context,
                course_context,
            )
        except Exception:
            return None

    def _write_comparison_sync(
        self, question: str, document_title: str, document_context: str, course_context: str
    ) -> str | None:
        assert self._client is not None
        response = self._client.chat.completions.create(
            model=self.settings.ai_model,
            temperature=0.2,
            max_tokens=1100,
            messages=[
                {"role": "system", "content": COMPARE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"CÂU HỎI:\n{question}\n\n"
                        f"TÀI LIỆU NGƯỜI HỌC: {document_title}\n{document_context}\n\n"
                        f"KIẾN THỨC KHÓA HỌC:\n{course_context}"
                    ),
                },
            ],
        )
        content = response.choices[0].message.content
        return content.strip() if content else None

    def _write_answer_sync(self, question: str, context: str) -> str | None:
        assert self._client is not None
        response = self._client.chat.completions.create(
            model=self.settings.ai_model,
            temperature=0.2,
            max_tokens=900,
            messages=[
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": f"QUESTION:\n{question}\n\nCONTEXT:\n{context}"},
            ],
        )
        content = response.choices[0].message.content
        return content.strip() if content else None

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

    @staticmethod
    def build_answer_context(hits: list[SearchHit], minimum_score: float = 0.45) -> str:
        sections = []
        for index, hit in enumerate(hits, start=1):
            if hit.score < minimum_score:
                continue
            text = hit.chunk.text.strip()
            if text:
                sections.append(
                    f"[Nguồn {index} | {hit.chunk.title}]\n{text[:2200]}"
                )
        return "\n\n---\n\n".join(sections)[:18000]
