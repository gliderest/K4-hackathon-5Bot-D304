from dataclasses import dataclass

from backend.app.memory.progress_store import SqliteProgressStore
from backend.app.rag.citation import build_citation
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.schemas.progress import LessonProgress, ProgressPatch
from backend.app.tools.search_document import SearchDocumentTool


@dataclass(slots=True)
class TutorAgent:
    search_document: SearchDocumentTool
    progress_store: SqliteProgressStore

    async def run(self, request: ChatRequest) -> ChatResponse:
        if len(request.message.strip()) < 8:
            return ChatResponse(
                answer="Bạn hãy mô tả rõ hơn câu hỏi để mình tìm đúng lesson, transcript hoặc slide liên quan.",
                confidence="low",
                needs_clarification=True,
                suggested_next_action=None,
            )

        # current_lesson_id only records progress. Retrieval always searches the
        # complete course corpus, so a concept can be found in any Day/Lesson.
        search_result = await self.search_document.search(
            keyword=request.message,
            course_id=request.course_id,
            learner_id=request.learner_id,
            document_ids=request.uploaded_document_ids,
            top_k=12,
        )
        combined_hits = self._select_diverse_sources(
            search_result.course_hits,
            search_result.upload_hits,
            limit=6,
        )

        if not combined_hits:
            return ChatResponse(
                answer=(
                    "Mình chưa tìm thấy đoạn học liệu khớp mạnh với câu hỏi này. "
                    "Bạn thử nói rõ hơn tên bài học, khái niệm, hoặc upload thêm tài liệu riêng để mình đối chiếu."
                ),
                confidence="low",
                needs_clarification=True,
                suggested_next_action=None,
            )

        citations = [build_citation(hit) for hit in combined_hits[:4]]
        answer = self._compose_answer(combined_hits)
        confidence = "high" if combined_hits[0].score >= 0.72 else "medium"

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
            suggested_next_action=None,
        )

    @staticmethod
    def _select_diverse_sources(course_hits: list, upload_hits: list, limit: int) -> list:
        """Keep high-scoring results while retaining Slide and Script evidence."""
        ranked_hits = sorted([*course_hits, *upload_hits], key=lambda hit: hit.score, reverse=True)
        selected = []
        selected_ids = set()
        for source_type in ("slide", "transcript", "user_upload"):
            hit = next((item for item in ranked_hits if item.chunk.source_type == source_type), None)
            if hit:
                selected.append(hit)
                selected_ids.add(hit.chunk.chunk_id)
        for hit in ranked_hits:
            if len(selected) >= limit:
                break
            if hit.chunk.chunk_id not in selected_ids:
                selected.append(hit)
                selected_ids.add(hit.chunk.chunk_id)
        return sorted(selected, key=lambda hit: hit.score, reverse=True)[:limit]

    @staticmethod
    def _compose_answer(hits: list) -> str:
        evidence_lines = []
        for hit in hits[:4]:
            snippet = hit.chunk.text.strip().replace("\n", " ")
            source_name = {
                "slide": "Slide",
                "transcript": "Script",
                "user_upload": "Tài liệu đã tải lên",
            }[hit.chunk.source_type]
            evidence_lines.append(
                f"- [{source_name}] {hit.chunk.title}: {snippet[:280]}{'...' if len(snippet) > 280 else ''}"
            )
        return "\n".join([
            "Mình đã tìm trong toàn bộ Slide và Script của khóa học. Các nguồn phù hợp nhất là:",
            *evidence_lines,
        ])
