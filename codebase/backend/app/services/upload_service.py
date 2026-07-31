import json
import re
from pathlib import Path
from uuid import uuid4

import fitz
from docx import Document
from fastapi import UploadFile

from backend.app.core.config import Settings
from backend.app.rag.embeddings import OpenAIEmbeddingService
from backend.app.schemas.upload import UploadResponse


TOKEN_PATTERN = re.compile(r"[0-9A-Za-zA-ZÀ-ỹ]+", re.UNICODE)


class UploadService:
    def __init__(
        self,
        settings: Settings,
        embedding_service: OpenAIEmbeddingService | None = None,
    ) -> None:
        self.settings = settings
        self.embedding_service = embedding_service

    async def save_upload(self, learner_id: str, file: UploadFile) -> UploadResponse:
        self._validate_upload(file)
        learner_dir = self.settings.resolve_path(self.settings.user_upload_dir) / learner_id
        learner_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(file.filename or "upload.txt").suffix.lower()
        document_id = f"doc-{uuid4().hex[:8]}"
        stored_name = f"{document_id}{suffix}"
        binary = await file.read()
        target_file = learner_dir / stored_name
        target_file.write_bytes(binary)

        text = self._extract_text(target_file)
        chunks = self._chunk_upload_text(
            document_id=document_id,
            source_file=stored_name,
            title=file.filename or stored_name,
            text=text,
        )
        if chunks and self.embedding_service and self.embedding_service.enabled:
            embeddings = await self.embedding_service.embed_texts([chunk["text"] for chunk in chunks])
            for chunk, embedding in zip(chunks, embeddings, strict=False):
                chunk["embedding"] = embedding

        metadata_file = learner_dir / f"{document_id}.chunks.json"
        metadata_file.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

        return UploadResponse(
            learner_id=learner_id,
            document_id=document_id,
            file_name=file.filename or stored_name,
            viewer_path=f"/api/assets/uploads/{learner_id}/{stored_name}",
            chunk_count=len(chunks),
        )

    def _validate_upload(self, file: UploadFile) -> None:
        file_name = file.filename or ""
        suffix = Path(file_name).suffix.lower()
        if suffix not in {".pdf", ".docx", ".txt", ".md"}:
            raise ValueError("Chỉ hỗ trợ file .pdf, .docx, .txt, .md")

    def _extract_text(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            return path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".docx":
            document = Document(path)
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
        if suffix == ".pdf":
            with fitz.open(path) as document:
                return "\n".join(page.get_text("text") for page in document)
        raise ValueError("Unsupported upload type")

    def _chunk_upload_text(
        self,
        document_id: str,
        source_file: str,
        title: str,
        text: str,
    ) -> list[dict[str, object]]:
        normalized = " ".join(text.split())
        if not normalized:
            return []
        words = normalized.split(" ")
        chunks: list[dict[str, object]] = []
        chunk_size = 120
        for index in range(0, len(words), chunk_size):
            snippet = " ".join(words[index : index + chunk_size]).strip()
            if len(snippet) < 20:
                continue
            chunks.append(
                {
                    "chunk_id": f"{document_id}-chunk-{len(chunks) + 1:03d}",
                    "text": snippet,
                    "title": title,
                    "source_file": source_file,
                    "metadata": {
                        "tokens": " ".join(
                            sorted({token.lower() for token in TOKEN_PATTERN.findall(snippet)})
                        )
                    },
                }
            )
        return chunks
