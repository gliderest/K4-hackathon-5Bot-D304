from dataclasses import dataclass

from backend.app.memory.progress_store import SqliteProgressStore
from backend.app.rag.citation import build_citation
from backend.app.rag.retriever import LocalRetriever
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.schemas.progress import LessonProgress, ProgressPatch


@dataclass(slots=True)
class TutorAgent:
    retriever: LocalRetriever
    progress_store: SqliteProgressStore

    async def run(self, request: ChatRequest) -> ChatResponse:
        if len(request.message.strip()) < 8:
            return ChatResponse(
                answer="Bạn hãy mô tả rõ hơn câu hỏi để mình tìm đúng lesson, transcript hoặc slide liên quan.",
                confidence="low",
                needs_clarification=True,
                suggested_next_action="Nếu có thể, hãy nhắc đến chủ đề, Day/Lesson, hoặc ví dụ bạn đang cần ôn lại.",
            )

        course_hits = await self.retriever.search_course(
            query=request.message,
            course_id=request.course_id,
            top_k=6,
        )
        upload_hits = await self.retriever.search_uploads(
            query=request.message,
            learner_id=request.learner_id,
            document_ids=request.uploaded_document_ids,
            top_k=3,
        )
        combined_hits = sorted(
            [*course_hits, *upload_hits],
            key=lambda hit: hit.score,
            reverse=True,
        )[:6]
        memory_context = await self.progress_store.build_context(
            learner_id=request.learner_id,
            course_id=request.course_id,
        )

        if not combined_hits:
            return ChatResponse(
                answer=(
                    "Mình chưa tìm thấy đoạn học liệu khớp mạnh với câu hỏi này. "
                    "Bạn thử nói rõ hơn tên bài học, khái niệm, hoặc upload thêm tài liệu riêng để mình đối chiếu."
                ),
                confidence="low",
                needs_clarification=True,
                suggested_next_action="Thử đặt câu hỏi cụ thể hơn theo dạng: 'Trong lesson nào nói về ...?'",
            )

        citations = [build_citation(hit) for hit in combined_hits[:4]]
        answer = self._compose_answer(message=request.message, memory_context=memory_context, hits=combined_hits)
        confidence = "high" if combined_hits[0].score >= 0.72 else "medium"
        next_action = f"Mở {citations[0].label} để xem đúng nguồn và tiếp tục ôn tập." if citations else None

        if request.current_lesson_id:
            await self.progress_store.update(
                learner_id=request.learner_id,
                patch=ProgressPatch(
                    course_id=request.course_id,
                    lesson=LessonProgress(
                        lesson_id=request.current_lesson_id,
                        completion_percent=20,
                        last_position=request.message[:120],
                    ),
                    add_review_items=[combined_hits[0].chunk.title],
                ),
            )

        return ChatResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            needs_clarification=False,
            suggested_next_action=next_action,
        )

    def _compose_answer(self, message: str, memory_context: str, hits: list) -> str:
        top_hits = hits[:3]
        evidence_lines = []
        for index, hit in enumerate(top_hits, start=1):
            snippet = hit.chunk.text.strip().replace("\n", " ")
            evidence_lines.append(
                f"{index}. {hit.chunk.title}: {snippet[:280]}{'...' if len(snippet) > 280 else ''}"
            )

        answer_parts = [
            "Tóm tắt từ học liệu liên quan nhất:",
            *evidence_lines,
            "",
            "Gợi ý học tiếp:",
            "Bạn nên mở các citation để xem đúng trang slide hoặc đoạn transcript rồi đối chiếu với phần đang học.",
            "Nếu bạn đang ôn quiz/lab, hãy hỏi tiếp theo dạng 'bài này nằm ở lesson nào' hoặc 'tóm tắt lại thành 3 ý chính'.",
            "",
            "Ngữ cảnh tiến độ hiện tại:",
            memory_context,
            "",
            f"Câu hỏi gốc: {message}",
        ]
        return "\n".join(answer_parts)
