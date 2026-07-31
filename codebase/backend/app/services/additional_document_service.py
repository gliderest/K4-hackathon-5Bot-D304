"""Two-step upload workflow for documents shared across the course."""

import json
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from backend.app.core.config import Settings
from backend.app.memory.additional_document_store import SqliteAdditionalDocumentStore
from backend.app.schemas.additional_document import AdditionalDocument, StagedAdditionalDocument


class AdditionalDocumentService:
    allowed_extensions = {".pdf", ".docx", ".txt", ".md"}

    def __init__(self, settings: Settings, store: SqliteAdditionalDocumentStore) -> None:
        self.settings = settings
        self.store = store

    async def stage(self, file: UploadFile) -> StagedAdditionalDocument:
        file_name = file.filename or "tai-lieu.txt"
        suffix = Path(file_name).suffix.lower()
        if suffix not in self.allowed_extensions:
            raise ValueError("Chỉ hỗ trợ file .pdf, .docx, .txt, .md")
        stage_id = f"stage-{uuid4().hex}"
        pending_dir = self.settings.resolve_path(self.settings.pending_additional_documents_dir)
        pending_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{stage_id}{suffix}"
        (pending_dir / stored_name).write_bytes(await file.read())
        (pending_dir / f"{stage_id}.json").write_text(
            json.dumps({"file_name": file_name, "stored_name": stored_name}, ensure_ascii=False),
            encoding="utf-8",
        )
        return StagedAdditionalDocument(
            stage_id=stage_id,
            file_name=file_name,
            viewer_path=f"/api/assets/pending-additional-documents/{stored_name}",
        )

    async def confirm(self, stage_id: str) -> AdditionalDocument:
        pending_dir = self.settings.resolve_path(self.settings.pending_additional_documents_dir)
        meta_path = pending_dir / f"{stage_id}.json"
        if not meta_path.exists():
            raise ValueError("Bản nháp tài liệu không tồn tại hoặc đã hết hạn")
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        source_path = pending_dir / metadata["stored_name"]
        if not source_path.exists():
            raise ValueError("Không tìm thấy file bản nháp")
        shared_dir = self.settings.resolve_path(self.settings.additional_documents_dir)
        shared_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid4().hex}{source_path.suffix.lower()}"
        target_path = shared_dir / stored_name
        source_path.replace(target_path)
        meta_path.unlink(missing_ok=True)
        return await self.store.add(
            title=Path(metadata["file_name"]).stem,
            file_name=metadata["file_name"],
            stored_name=stored_name,
        )

    async def cancel(self, stage_id: str) -> None:
        pending_dir = self.settings.resolve_path(self.settings.pending_additional_documents_dir)
        meta_path = pending_dir / f"{stage_id}.json"
        if not meta_path.exists():
            return
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        (pending_dir / metadata["stored_name"]).unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)
