"""Build context from an open upload and related course sources."""

from dataclasses import dataclass

from backend.app.rag.contracts import SearchHit
from backend.app.rag.retriever import LocalRetriever
from backend.app.schemas.chat import CurrentDocument


@dataclass(slots=True)
class CompareDocumentResult:
    document_hits: list[SearchHit]
    course_hits: list[SearchHit]


@dataclass(slots=True)
class CompareDocumentWithCourseTool:
    retriever: LocalRetriever

    async def compare(
        self,
        question: str,
        document: CurrentDocument,
        learner_id: str,
        document_ids: list[str],
        conversation_id: str | None,
    ) -> CompareDocumentResult:
        document_chunks = await self.retriever.get_document_chunks(
            source_type=document.source_type,
            source_id=document.source_id,
            learner_id=learner_id,
            document_ids=document_ids,
            conversation_id=conversation_id,
        )
        document_hits = [SearchHit(chunk=chunk, score=1.0) for chunk in document_chunks]
        query_context = " ".join(hit.chunk.text[:500] for hit in document_hits[:8])
        course_hits = await self.retriever.search_course(
            query=f"{question}\n{query_context}",
            course_id=document_chunks[0].course_id if document_chunks else "",
            top_k=8,
        )
        return CompareDocumentResult(
            document_hits=document_hits[:12],
            course_hits=course_hits,
        )
