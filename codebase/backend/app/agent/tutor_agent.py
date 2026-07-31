from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from backend.app.agent.request_router import ToolRoute, choose_tool_route
from backend.app.agent.safety_router import (
    MessageScope,
    OUT_OF_SCOPE_RESPONSE,
    classify_message_scope,
)
from backend.app.memory.progress_store import SqliteProgressStore
from backend.app.rag.citation import build_citation
from backend.app.schemas.chat import Citation, ChatRequest, ChatResponse, ToolTraceEvent
from backend.app.schemas.progress import LessonProgress, ProgressPatch
from backend.app.tools.search_document import SearchDocumentTool
from backend.app.tools.analyse_current_document import AnalyseCurrentDocumentTool
from backend.app.tools.search_web import SearchWebTool, WebSearchHit
from backend.app.services.document_writer import CurrentDocumentWriter
from backend.app.services.web_answer_writer import WebAnswerWriter


TraceCallback = Callable[[ToolTraceEvent], Awaitable[None]]


@dataclass(slots=True)
class TutorAgent:
    search_document: SearchDocumentTool
    analyse_current_document: AnalyseCurrentDocumentTool
    search_web: SearchWebTool
    web_search_fallback_min_score: float
    current_document_writer: CurrentDocumentWriter
    web_answer_writer: WebAnswerWriter
    progress_store: SqliteProgressStore

    async def run(
        self,
        request: ChatRequest,
        on_trace: TraceCallback | None = None,
    ) -> ChatResponse:
        tool_trace: list[ToolTraceEvent] = []

        async def record(
            tool_name: str,
            status: str,
            summary: str,
            result_count: int | None = None,
        ) -> None:
            event = ToolTraceEvent(
                tool_name=tool_name,
                status=status,
                summary=summary,
                result_count=result_count,
            )
            tool_trace.append(event)
            if on_trace is not None:
                await on_trace(event)

        scope = classify_message_scope(request.message, request.current_document)
        if scope in {MessageScope.OUT_OF_SCOPE, MessageScope.PROMPT_INJECTION}:
            return ChatResponse(
                answer=OUT_OF_SCOPE_RESPONSE,
                tool_trace=tool_trace,
                confidence="low",
                needs_clarification=False,
                suggested_next_action=None,
            )

        if len(request.message.strip()) < 8:
            return ChatResponse(
                answer="Bạn hãy mô tả rõ hơn câu hỏi để mình tìm đúng lesson, transcript hoặc slide liên quan.",
                tool_trace=tool_trace,
                confidence="low",
                needs_clarification=True,
                suggested_next_action=None,
            )

        route = choose_tool_route(request.message, request.current_document)
        if route is ToolRoute.ANALYSE_CURRENT_DOCUMENT:
            return await self._analyse_open_document(request, tool_trace, record)

        # current_lesson_id only records progress. Cross-document retrieval runs
        # only when the learner asks to find knowledge outside the open document.
        await record(
            "search_document",
            "started",
            "Đang tìm trong toàn bộ Slide, Script và tài liệu đã tải lên của cuộc hội thoại này.",
        )
        search_result = await self.search_document.search(
            keyword=request.message,
            course_id=request.course_id,
            learner_id=request.learner_id,
            document_ids=request.uploaded_document_ids,
            conversation_id=request.conversation_id,
            top_k=12,
        )
        await record(
            "search_document",
            "completed",
            (
                "Đã tìm thấy "
                f"{len(search_result.course_hits)} đoạn trong học liệu khóa học và "
                f"{len(search_result.upload_hits)} đoạn trong tài liệu đã tải lên."
            ),
            result_count=len(search_result.course_hits) + len(search_result.upload_hits),
        )
        combined_hits = self._select_diverse_sources(
            search_result.course_hits,
            search_result.upload_hits,
            limit=6,
        )

        best_internal_score = max((hit.score for hit in combined_hits), default=0.0)
        should_search_web = (
            not combined_hits
            or best_internal_score < self.web_search_fallback_min_score
        )
        if should_search_web:
            fallback_reason = (
                "Không có kết quả trong học liệu và ngữ cảnh hội thoại"
                if not combined_hits
                else (
                    "Kết quả nội bộ có độ khớp cao nhất "
                    f"{best_internal_score:.2f}, thấp hơn ngưỡng "
                    f"{self.web_search_fallback_min_score:.2f}"
                )
            )
            await record(
                "search_web",
                "started",
                f"{fallback_reason}; đang tìm nguồn trên web.",
            )
            web_result = await self.search_web.search(request.message)
            if web_result.hits:
                await record(
                    "search_web",
                    "completed",
                    f"Đã tìm thấy {len(web_result.hits)} nguồn web bên ngoài học liệu.",
                    result_count=len(web_result.hits),
                )
                answer = await self.web_answer_writer.write(
                    question=request.message,
                    hits=web_result.hits,
                )
                return ChatResponse(
                    answer=answer or self._compose_web_answer(web_result.hits),
                    citations=self._build_web_citations(web_result.hits),
                    tool_trace=tool_trace,
                    confidence="medium",
                    needs_clarification=False,
                    suggested_next_action=None,
                )

            web_status = (
                web_result.message
                or "Không tìm thấy nguồn web phù hợp cho từ khóa này."
            )
            await record(
                "search_web",
                "completed",
                web_status,
                result_count=0,
            )
            return ChatResponse(
                answer=(
                    "Mình chưa tìm thấy nguồn đủ tin cậy trong học liệu, ngữ cảnh hội thoại "
                    f"hoặc web. {web_status}"
                ),
                tool_trace=tool_trace,
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
            tool_trace=tool_trace,
            confidence=confidence,
            needs_clarification=False,
            suggested_next_action=None,
        )

    async def _analyse_open_document(
        self,
        request: ChatRequest,
        tool_trace: list[ToolTraceEvent],
        record: TraceCallback,
    ) -> ChatResponse:
        if request.current_document is None:
            return ChatResponse(
                answer="Bạn hãy mở tài liệu cần tóm tắt hoặc giải thích trước, rồi gửi lại câu hỏi.",
                tool_trace=tool_trace,
                confidence="low",
                needs_clarification=True,
                suggested_next_action=None,
            )

        await record(
            "analyse_current_document",
            "started",
            f"Đang đọc nội dung tài liệu đang mở: {request.current_document.title}.",
        )
        analysis = await self.analyse_current_document.analyse(
            document=request.current_document,
            learner_id=request.learner_id,
            document_ids=request.uploaded_document_ids,
            conversation_id=request.conversation_id,
        )
        await record(
            "analyse_current_document",
            "completed",
            f"Đã lấy {len(analysis.chunks)} đoạn nội dung từ tài liệu đang mở để phân tích.",
            result_count=len(analysis.chunks),
        )
        if not analysis.chunks:
            return ChatResponse(
                answer="Mình chưa đọc được nội dung của tài liệu đang mở. Bạn thử chọn lại tài liệu hoặc tải lại trang.",
                tool_trace=tool_trace,
                confidence="low",
                needs_clarification=True,
                suggested_next_action=None,
            )

        answer = await self.current_document_writer.write(
            question=request.message,
            document_title=request.current_document.title,
            hits=analysis.chunks,
        )
        if answer is None:
            answer = self._compose_current_document_fallback(
                title=request.current_document.title,
                hits=analysis.chunks,
            )
        return ChatResponse(
            answer=answer,
            citations=[],
            tool_trace=tool_trace,
            confidence="high",
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

    @staticmethod
    def _build_web_citations(hits: list[WebSearchHit]) -> list[Citation]:
        return [
            Citation(
                label=hit.title,
                source_type="web",
                source_id=hit.url,
                viewer_path=hit.url,
                score=None,
            )
            for hit in hits[:4]
        ]

    @staticmethod
    def _compose_web_answer(hits: list[WebSearchHit]) -> str:
        sources = []
        for hit in hits[:4]:
            snippet = hit.snippet.replace("\n", " ").strip()
            sources.append(
                f"- {hit.title}: {snippet[:300]}{'...' if len(snippet) > 300 else ''}"
            )
        return "\n".join([
            "Mình không tìm thấy nội dung này trong học liệu hoặc ngữ cảnh hội thoại, "
            "nên đã tham khảo các nguồn web sau:",
            *sources,
        ])

    @staticmethod
    def _compose_current_document_fallback(title: str, hits: list) -> str:
        points = []
        for hit in hits[:6]:
            text = hit.chunk.text.replace("\n", " ").strip()
            text = text.replace("Nội dung slide: ", "")
            points.append(text[:240] + ("..." if len(text) > 240 else ""))
        return "\n".join([
            f"Tóm lược tài liệu đang mở — {title}:",
            "\n".join(f"- {point}" for point in points),
        ])
