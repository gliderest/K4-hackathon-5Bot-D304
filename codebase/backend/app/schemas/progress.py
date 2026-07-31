from datetime import datetime

from pydantic import BaseModel, Field


class LessonProgress(BaseModel):
    lesson_id: str
    completion_percent: int = Field(ge=0, le=100)
    last_position: str | None = None
    last_seen_at: datetime | None = None


class ProgressSnapshot(BaseModel):
    learner_id: str
    course_id: str
    lessons: list[LessonProgress] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    review_queue: list[str] = Field(default_factory=list)


class ProgressPatch(BaseModel):
    course_id: str
    lesson: LessonProgress | None = None
    add_weak_topics: list[str] = Field(default_factory=list)
    add_review_items: list[str] = Field(default_factory=list)


class UploadRecord(BaseModel):
    document_id: str
    file_name: str
    viewer_path: str
    chunk_count: int
