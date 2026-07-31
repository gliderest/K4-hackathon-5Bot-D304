import pytest

from backend.app.rag.contracts import SourceChunk
from backend.app.schemas.chat import CurrentDocument
from backend.app.tools.compare_document import CompareDocumentWithCourseTool


class FakeRetriever:
    async def get_document_chunks(self, **_):
        return [SourceChunk("upload-1", "Bài làm nói về ReAct.", "vlearn-hackathon", "upload", "Bài làm", "user_upload", "my.md")]

    async def search_course(self, **kwargs):
        assert "ReAct" in kwargs["query"]
        return [SourceChunk("course-1", "ReAct gồm Thought, Action, Observation.", "vlearn-hackathon", "lesson-1", "ReAct", "transcript", "lesson.md")]


@pytest.mark.asyncio
async def test_compare_tool_reads_upload_and_searches_course():
    result = await CompareDocumentWithCourseTool(FakeRetriever()).compare(
        question="So sánh ReAct",
        document=CurrentDocument(source_type="user_upload", source_id="my.md", title="Bài làm"),
        learner_id="learner-1",
        document_ids=["my.md"],
        conversation_id="conversation-1",
    )

    assert len(result.document_hits) == 1
    assert len(result.course_hits) == 1
