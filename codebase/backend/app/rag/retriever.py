from rapidfuzz import fuzz

from backend.app.core.config import Settings
from backend.app.rag.contracts import SearchHit, SourceChunk
from backend.app.rag.embeddings import OpenAIEmbeddingService, cosine_similarity
from backend.app.rag.ingestion import CourseCorpus, tokenize


class LocalRetriever:
    def __init__(
        self,
        settings: Settings,
        corpus: CourseCorpus,
        embedding_service: OpenAIEmbeddingService | None = None,
    ) -> None:
        self.settings = settings
        self.corpus = corpus
        self.embedding_service = embedding_service

    async def search_course(
        self,
        query: str,
        course_id: str,
        top_k: int,
    ) -> list[SearchHit]:
        if course_id != self.settings.course_id:
            return []
        return await self._search_with_provider(
            query=query,
            chunks=self.corpus.course_chunks,
            top_k=top_k,
            vectors=self.corpus.chunk_vectors,
        )

    async def search_uploads(
        self,
        query: str,
        learner_id: str,
        document_ids: list[str],
        conversation_id: str | None,
        top_k: int,
    ) -> list[SearchHit]:
        chunks, vectors = await self._load_upload_chunks(
            learner_id=learner_id,
            document_ids=document_ids,
            conversation_id=conversation_id,
        )
        return await self._search_with_provider(
            query=query,
            chunks=chunks,
            top_k=top_k,
            vectors=vectors,
        )

    async def get_document_chunks(
        self,
        source_type: str,
        source_id: str,
        learner_id: str,
        document_ids: list[str],
        conversation_id: str | None,
    ) -> list[SourceChunk]:
        """Return chunks from one named source, without searching other documents."""
        if source_type in {"slide", "transcript"}:
            chunks = [
                chunk
                for chunk in self.corpus.course_chunks
                if chunk.source_type == source_type and chunk.source_file == source_id
            ]
            # Page overviews contain the complete page and avoid duplicate block text
            # when the learner asks to summarize the currently open PDF.
            if source_type == "slide":
                overview_chunks = [chunk for chunk in chunks if chunk.chunk_id.endswith(":overview")]
                return overview_chunks or chunks
            return chunks

        upload_chunks, _ = await self._load_upload_chunks(
            learner_id=learner_id,
            document_ids=document_ids,
            conversation_id=conversation_id,
        )
        return [chunk for chunk in upload_chunks if chunk.source_file == source_id]

    async def _load_upload_chunks(
        self,
        learner_id: str,
        document_ids: list[str],
        conversation_id: str | None,
    ) -> tuple[list[SourceChunk], dict[str, list[float]]]:
        if not conversation_id:
            return [], {}
        conversation_dir = (
            self.settings.resolve_path(self.settings.user_upload_dir) / learner_id / conversation_id
        )
        if not conversation_dir.exists():
            return [], {}
        allowed = set(document_ids)
        chunks: list[SourceChunk] = []
        vectors: dict[str, list[float]] = {}
        for metadata_file in conversation_dir.glob("*.chunks.json"):
            doc_id = metadata_file.stem.replace(".chunks", "")
            if allowed and doc_id not in allowed:
                continue
            payload = metadata_file.read_text(encoding="utf-8")
            for item in __import__("json").loads(payload):
                if item.get("embedding"):
                    vectors[item["chunk_id"]] = item["embedding"]
                chunks.append(
                    SourceChunk(
                        chunk_id=item["chunk_id"],
                        text=item["text"],
                        course_id=self.settings.course_id,
                        lesson_id=item.get("lesson_id") or "user-upload",
                        title=item["title"],
                        source_type="user_upload",
                        source_file=item["source_file"],
                        page=item.get("page"),
                        segment_id=item.get("segment_id"),
                        owner_learner_id=learner_id,
                        metadata={
                            **item.get("metadata", {}),
                            "conversation_id": conversation_id,
                        },
                    )
                )
        return chunks, vectors

    async def _search_with_provider(
        self,
        query: str,
        chunks: list[SourceChunk],
        top_k: int,
        vectors: dict[str, list[float]],
    ) -> list[SearchHit]:
        if not self.embedding_service or not self.embedding_service.enabled:
            return self._search_with_vectors(
                query=query,
                chunks=chunks,
                top_k=top_k,
                vectors=vectors,
            )

        query_vector = (await self.embedding_service.embed_texts([query]))[0]
        return self._search_with_vectors(
            query=query,
            chunks=chunks,
            top_k=top_k,
            vectors=vectors,
            query_vector=query_vector,
        )

    def _search_with_vectors(
        self,
        query: str,
        chunks: list[SourceChunk],
        top_k: int,
        vectors: dict[str, list[float]],
        query_vector: list[float] | None = None,
    ) -> list[SearchHit]:
        query_tokens = tokenize(query)
        hits: list[SearchHit] = []
        for chunk in chunks:
            chunk_tokens = tokenize(chunk.text)
            overlap = len(query_tokens & chunk_tokens) / max(len(query_tokens), 1)
            fuzzy = fuzz.partial_ratio(query.lower(), chunk.text.lower()) / 100
            title_boost = 0.15 if any(token in tokenize(chunk.title) for token in query_tokens) else 0.0
            if query_vector is not None:
                embedding_score = max(
                    0.0,
                    cosine_similarity(query_vector, vectors.get(chunk.chunk_id, [])),
                )
                score = round(
                    (embedding_score * 0.6) + (overlap * 0.25) + (fuzzy * 0.15) + title_boost,
                    4,
                )
            else:
                score = round((overlap * 0.65) + (fuzzy * 0.35) + title_boost, 4)
            if score < self.settings.rag_min_score:
                continue
            hits.append(SearchHit(chunk=chunk, score=score))
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:top_k]
