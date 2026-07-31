"""Search all course documents from a learner's keyword or natural-language question."""

from dataclasses import dataclass

from backend.app.rag.contracts import SearchHit
from backend.app.rag.retriever import LocalRetriever


@dataclass(slots=True)
class SearchDocumentResult:
    course_hits: list[SearchHit]
    upload_hits: list[SearchHit]


@dataclass(slots=True)
class SearchDocumentTool:
    """Retrieval tool for every indexed Slide, Script, and selected upload."""

    retriever: LocalRetriever

    async def search(
        self,
        keyword: str,
        course_id: str,
        learner_id: str,
        document_ids: list[str] | None = None,
        conversation_id: str | None = None,
        top_k: int = 12,
    ) -> SearchDocumentResult:
        query = keyword.strip()
        if not query:
            return SearchDocumentResult(course_hits=[], upload_hits=[])

        course_hits = await self.retriever.search_course(
            query=query,
            course_id=course_id,
            top_k=top_k,
        )
        upload_hits = await self.retriever.search_uploads(
            query=query,
            learner_id=learner_id,
            document_ids=document_ids or [],
            conversation_id=conversation_id,
            top_k=min(3, top_k),
        )
        return SearchDocumentResult(course_hits=course_hits, upload_hits=upload_hits)
