import json
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from backend.app.schemas.progress import LessonProgress, ProgressPatch, ProgressSnapshot


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SqliteProgressStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    async def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.database_path) as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS learner_progress (
                    learner_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (learner_id, course_id)
                )
                """
            )
            await connection.commit()

    async def get(self, learner_id: str, course_id: str) -> ProgressSnapshot:
        async with aiosqlite.connect(self.database_path) as connection:
            cursor = await connection.execute(
                """
                SELECT payload
                FROM learner_progress
                WHERE learner_id = ? AND course_id = ?
                """,
                (learner_id, course_id),
            )
            row = await cursor.fetchone()
        if not row:
            return ProgressSnapshot(learner_id=learner_id, course_id=course_id)
        return ProgressSnapshot.model_validate(json.loads(row[0]))

    async def update(self, learner_id: str, patch: ProgressPatch) -> ProgressSnapshot:
        snapshot = await self.get(learner_id=learner_id, course_id=patch.course_id)
        lesson_map = {lesson.lesson_id: lesson for lesson in snapshot.lessons}

        if patch.lesson:
            existing = lesson_map.get(patch.lesson.lesson_id)
            if existing:
                lesson_map[patch.lesson.lesson_id] = LessonProgress(
                    lesson_id=patch.lesson.lesson_id,
                    completion_percent=max(
                        existing.completion_percent, patch.lesson.completion_percent
                    ),
                    last_position=patch.lesson.last_position or existing.last_position,
                    last_seen_at=patch.lesson.last_seen_at or utcnow(),
                )
            else:
                lesson = patch.lesson.model_copy()
                if lesson.last_seen_at is None:
                    lesson.last_seen_at = utcnow()
                lesson_map[lesson.lesson_id] = lesson

        weak_topics = list(
            dict.fromkeys(
                [*snapshot.weak_topics, *patch.add_weak_topics]
            )
        )
        review_queue = list(
            dict.fromkeys(
                [*snapshot.review_queue, *patch.add_review_items]
            )
        )

        updated = ProgressSnapshot(
            learner_id=learner_id,
            course_id=patch.course_id,
            lessons=sorted(lesson_map.values(), key=lambda lesson: lesson.lesson_id),
            weak_topics=weak_topics[:12],
            review_queue=review_queue[:20],
        )
        payload = updated.model_dump_json()
        async with aiosqlite.connect(self.database_path) as connection:
            await connection.execute(
                """
                INSERT INTO learner_progress (learner_id, course_id, payload, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(learner_id, course_id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (learner_id, patch.course_id, payload, utcnow().isoformat()),
            )
            await connection.commit()
        return updated

    async def build_context(self, learner_id: str, course_id: str) -> str:
        snapshot = await self.get(learner_id=learner_id, course_id=course_id)
        if not snapshot.lessons and not snapshot.weak_topics and not snapshot.review_queue:
            return "Chưa có dữ liệu tiến độ cho người học này."
        lesson_parts = [
            f"{lesson.lesson_id}: {lesson.completion_percent}% hoàn thành"
            for lesson in snapshot.lessons[:6]
        ]
        weak_topics = ", ".join(snapshot.weak_topics[:6]) or "không có"
        review_items = ", ".join(snapshot.review_queue[:6]) or "không có"
        return (
            "Tiến độ người học:\n"
            f"- Lessons: {'; '.join(lesson_parts) or 'chưa học'}\n"
            f"- Weak topics: {weak_topics}\n"
            f"- Review queue: {review_items}"
        )
