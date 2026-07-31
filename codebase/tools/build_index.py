"""Build course embeddings index for local retrieval."""

import asyncio
from pathlib import Path
import sys


def _ensure_backend_on_path() -> None:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


async def _run() -> None:
    _ensure_backend_on_path()
    from backend.app.core.config import settings
    from backend.app.rag.embeddings import OpenAIEmbeddingService
    from backend.app.rag.ingestion import CourseCorpus

    embedding_service = OpenAIEmbeddingService(settings)
    if not embedding_service.enabled:
        raise RuntimeError(
            "Embeddings chua duoc bat. Hay set AI_PROVIDER=openai hoac openrouter, AI_API_KEY, EMBEDDING_MODEL."
        )

    corpus = CourseCorpus(settings, embedding_service=embedding_service)
    await corpus.build()
    print(
        f"Built {len(corpus.course_chunks)} course chunk embeddings with provider={settings.ai_provider} model={settings.embedding_model}."
    )


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
