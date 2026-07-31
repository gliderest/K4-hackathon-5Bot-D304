from typing import Literal

from pydantic import BaseModel, Field

from backend.app.schemas.chat import Citation, ToolTraceEvent


class ConversationSummary(BaseModel):
    conversation_id: str
    title: str
    created_at: str
    updated_at: str


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    citations: list[Citation] = Field(default_factory=list)
    tool_trace: list[ToolTraceEvent] = Field(default_factory=list)
    created_at: str


class ConversationDetail(BaseModel):
    conversation_id: str
    title: str
    messages: list[ConversationMessage] = Field(default_factory=list)
