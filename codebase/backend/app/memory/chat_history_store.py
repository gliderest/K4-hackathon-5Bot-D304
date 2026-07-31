"""Persistent conversation history for the VLearn tutor."""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import aiosqlite

from backend.app.schemas.chat import Citation, ToolTraceEvent
from backend.app.schemas.conversation import (
    ConversationDetail,
    ConversationMessage,
    ConversationSummary,
)


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SqliteChatHistoryStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    async def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.database_path) as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_conversations (
                    conversation_id TEXT PRIMARY KEY,
                    learner_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    citations_json TEXT NOT NULL DEFAULT '[]',
                    tool_trace_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES chat_conversations(conversation_id)
                )
                """
            )
            cursor = await connection.execute("PRAGMA table_info(chat_messages)")
            message_columns = {row[1] for row in await cursor.fetchall()}
            if "tool_trace_json" not in message_columns:
                await connection.execute(
                    """
                    ALTER TABLE chat_messages
                    ADD COLUMN tool_trace_json TEXT NOT NULL DEFAULT '[]'
                    """
                )
            await connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_conversations_learner
                ON chat_conversations(learner_id, course_id, updated_at DESC)
                """
            )
            await connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation
                ON chat_messages(conversation_id, id)
                """
            )
            await connection.commit()

    async def get_or_create(
        self,
        learner_id: str,
        course_id: str,
        first_message: str,
        conversation_id: str | None,
    ) -> str:
        if conversation_id:
            async with aiosqlite.connect(self.database_path) as connection:
                cursor = await connection.execute(
                    """
                    SELECT learner_id, course_id FROM chat_conversations
                    WHERE conversation_id = ?
                    """,
                    (conversation_id,),
                )
                existing = await cursor.fetchone()
            if existing:
                if existing[0] == learner_id and existing[1] == course_id:
                    return conversation_id
                raise ValueError("Không tìm thấy cuộc hội thoại của người học này.")

        new_id = conversation_id or str(uuid4())
        now = utcnow_iso()
        async with aiosqlite.connect(self.database_path) as connection:
            await connection.execute(
                """
                INSERT INTO chat_conversations (
                    conversation_id, learner_id, course_id, title, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (new_id, learner_id, course_id, first_message, now, now),
            )
            await connection.commit()
        return new_id

    async def append_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        citations: list[Citation] | None = None,
        tool_trace: list[ToolTraceEvent] | None = None,
    ) -> None:
        now = utcnow_iso()
        citation_json = json.dumps(
            [citation.model_dump(mode="json") for citation in citations or []],
            ensure_ascii=False,
        )
        tool_trace_json = json.dumps(
            [item.model_dump(mode="json") for item in tool_trace or []],
            ensure_ascii=False,
        )
        async with aiosqlite.connect(self.database_path) as connection:
            await connection.execute(
                """
                INSERT INTO chat_messages (
                    conversation_id, role, content, citations_json, tool_trace_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (conversation_id, role, content, citation_json, tool_trace_json, now),
            )
            await connection.execute(
                """
                UPDATE chat_conversations SET updated_at = ? WHERE conversation_id = ?
                """,
                (now, conversation_id),
            )
            await connection.commit()

    async def list_conversations(
        self,
        learner_id: str,
        course_id: str,
        limit: int = 30,
    ) -> list[ConversationSummary]:
        async with aiosqlite.connect(self.database_path) as connection:
            cursor = await connection.execute(
                """
                SELECT conversation_id, title, created_at, updated_at
                FROM chat_conversations
                WHERE learner_id = ? AND course_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (learner_id, course_id, limit),
            )
            rows = await cursor.fetchall()
        return [
            ConversationSummary(
                conversation_id=row[0], title=row[1], created_at=row[2], updated_at=row[3]
            )
            for row in rows
        ]

    async def get_conversation(
        self,
        conversation_id: str,
        learner_id: str,
        course_id: str,
    ) -> ConversationDetail | None:
        async with aiosqlite.connect(self.database_path) as connection:
            cursor = await connection.execute(
                """
                SELECT title FROM chat_conversations
                WHERE conversation_id = ? AND learner_id = ? AND course_id = ?
                """,
                (conversation_id, learner_id, course_id),
            )
            conversation = await cursor.fetchone()
            if not conversation:
                return None
            cursor = await connection.execute(
                """
                SELECT role, content, citations_json, tool_trace_json, created_at
                FROM chat_messages WHERE conversation_id = ? ORDER BY id ASC
                """,
                (conversation_id,),
            )
            rows = await cursor.fetchall()
        return ConversationDetail(
            conversation_id=conversation_id,
            title=conversation[0],
            messages=[
                ConversationMessage(
                    role=row[0],
                    content=row[1],
                    citations=[Citation.model_validate(item) for item in json.loads(row[2])],
                    tool_trace=[ToolTraceEvent.model_validate(item) for item in json.loads(row[3])],
                    created_at=row[4],
                )
                for row in rows
            ],
        )
