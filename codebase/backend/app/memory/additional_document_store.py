from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import aiosqlite

from backend.app.schemas.additional_document import AdditionalDocument


class SqliteAdditionalDocumentStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    async def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.database_path) as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS additional_documents (
                    document_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    stored_name TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                )
                """
            )
            await connection.commit()

    async def add(self, title: str, file_name: str, stored_name: str) -> AdditionalDocument:
        document_id = f"additional-{uuid4().hex[:12]}"
        created_at = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self.database_path) as connection:
            await connection.execute(
                """
                INSERT INTO additional_documents (document_id, title, file_name, stored_name, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (document_id, title, file_name, stored_name, created_at),
            )
            await connection.commit()
        return AdditionalDocument(
            document_id=document_id,
            title=title,
            file_name=file_name,
            viewer_path=f"/api/assets/additional-documents/{stored_name}",
            created_at=created_at,
        )

    async def list(self) -> list[AdditionalDocument]:
        async with aiosqlite.connect(self.database_path) as connection:
            cursor = await connection.execute(
                """
                SELECT document_id, title, file_name, stored_name, created_at
                FROM additional_documents ORDER BY created_at DESC
                """
            )
            rows = await cursor.fetchall()
        return [
            AdditionalDocument(
                document_id=row[0],
                title=row[1],
                file_name=row[2],
                viewer_path=f"/api/assets/additional-documents/{row[3]}",
                created_at=row[4],
            )
            for row in rows
        ]
