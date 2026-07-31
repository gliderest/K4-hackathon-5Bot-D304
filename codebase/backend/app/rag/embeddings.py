import asyncio
from pathlib import Path
from typing import Iterable

from openai import OpenAI

from backend.app.core.config import Settings


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(left_item * right_item for left_item, right_item in zip(left, right))
    left_norm = sum(item * item for item in left) ** 0.5
    right_norm = sum(item * item for item in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


class OpenAIEmbeddingService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        provider = settings.ai_provider.lower()
        self.enabled = (
            provider in {"openai", "openrouter"}
            and bool(settings.ai_api_key)
            and bool(settings.embedding_model)
        )
        self.provider = provider
        self._client = self._build_client() if self.enabled else None

    def _build_client(self) -> OpenAI:
        kwargs: dict[str, str] = {"api_key": self.settings.ai_api_key}
        base_url = self._resolve_base_url()
        if base_url:
            kwargs["base_url"] = base_url
        return OpenAI(**kwargs)

    def _resolve_base_url(self) -> str:
        if self.settings.ai_base_url:
            return self.settings.ai_base_url
        if self.provider == "openrouter":
            return "https://openrouter.ai/api/v1"
        return ""

    async def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        values = list(texts)
        if not values:
            return []
        if not self.enabled or self._client is None:
            raise RuntimeError("Embedding service is not enabled")
        return await asyncio.to_thread(self._embed_texts_sync, values)

    def _embed_texts_sync(self, texts: list[str]) -> list[list[float]]:
        assert self._client is not None
        vectors: list[list[float]] = []
        batch_size = max(1, self.settings.embedding_batch_size)
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            response = self._client.embeddings.create(
                model=self.settings.embedding_model,
                input=batch,
            )
            vectors.extend([item.embedding for item in response.data])
        return vectors


def vector_store_path(root: Path, file_name: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    return root / file_name
