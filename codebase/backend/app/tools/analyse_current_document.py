"""Read only the document currently open in the learner's viewer."""

from dataclasses import dataclass

from backend.app.rag.contracts import SearchHit, SourceChunk
from backend.app.rag.retriever import LocalRetriever
from backend.app.schemas.chat import CurrentDocument


@dataclass(slots=True)
class CurrentDocumentAnalysis:
    chunks: list[SearchHit]


@dataclass(slots=True)
class AnalyseCurrentDocumentTool:
    retriever: LocalRetriever

    async def analyse(
        self,
        document: CurrentDocument,
        learner_id: str,
        document_ids: list[str] | None = None,
        max_chunks: int = 12,
    ) -> CurrentDocumentAnalysis:
        chunks = await self.retriever.get_document_chunks(
            source_type=document.source_type,
            source_id=document.source_id,
            learner_id=learner_id,
            document_ids=document_ids or [],
        )
        selected = self._sample_chunks(chunks, max_chunks=max_chunks)
        return CurrentDocumentAnalysis(
            chunks=[SearchHit(chunk=chunk, score=1.0) for chunk in selected]
        )

    @staticmethod
    def _sample_chunks(chunks: list[SourceChunk], max_chunks: int) -> list[SourceChunk]:
        if len(chunks) <= max_chunks:
            return chunks
        # Sample across the file so a summary covers the beginning, middle, and end.
        indexes = {
            round(index * (len(chunks) - 1) / (max_chunks - 1))
            for index in range(max_chunks)
        }
        return [chunks[index] for index in sorted(indexes)]
