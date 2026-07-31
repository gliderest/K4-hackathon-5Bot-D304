from typing import Literal

from pydantic import BaseModel, Field


class ToolTraceEvent(BaseModel):
    """A user-facing activity entry for a tool call, not hidden model reasoning."""

    tool_name: Literal[
        "request_router",
        "search_document",
        "analyse_current_document",
        "search_web",
    ]
    status: Literal["started", "completed", "skipped"]
    summary: str
    result_count: int | None = None


class Citation(BaseModel):
    label: str
    source_type: Literal["slide", "transcript", "user_upload", "web"]
    source_id: str
    lesson_id: str | None = None
    page: int | None = None
    segment_id: str | None = None
    viewer_path: str
    score: float | None = None


class CurrentDocument(BaseModel):
    source_type: Literal["slide", "transcript", "user_upload"]
    source_id: str
    title: str
    lesson_id: str | None = None


class ChatRequest(BaseModel):
    learner_id: str
    course_id: str
    message: str = Field(min_length=1, max_length=4000)
    current_lesson_id: str | None = None
    current_document: CurrentDocument | None = None
    uploaded_document_ids: list[str] = Field(default_factory=list)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str = ""
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    tool_trace: list[ToolTraceEvent] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"]
    needs_clarification: bool = False
    suggested_next_action: str | None = None
