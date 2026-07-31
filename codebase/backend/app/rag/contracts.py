from dataclasses import dataclass, field
from typing import Literal


SourceType = Literal["slide", "transcript", "user_upload"]


@dataclass(slots=True)
class SourceChunk:
    chunk_id: str
    text: str
    course_id: str
    lesson_id: str
    title: str
    source_type: SourceType
    source_file: str
    page: int | None = None
    segment_id: str | None = None
    owner_learner_id: str | None = None
    metadata: dict[str, str | int | float | None] = field(default_factory=dict)


@dataclass(slots=True)
class LessonRecord:
    lesson_id: str
    title: str
    transcript_file: str
    transcript_markdown: str
    source_slide_file: str | None
    source_slide_label: str | None
    segment_ids: list[str]


@dataclass(slots=True)
class SearchHit:
    chunk: SourceChunk
    score: float
