from types import SimpleNamespace

import pytest

from backend.app.core.config import Settings
from backend.app.rag.contracts import SearchHit, SourceChunk
from backend.app.services.document_writer import CurrentDocumentWriter


def make_hit(text: str, score: float = 0.9) -> SearchHit:
    return SearchHit(
        chunk=SourceChunk(
            chunk_id="chunk-1",
            text=text,
            course_id="vlearn-hackathon",
            lesson_id="lesson-1",
            title="Lesson 1",
            source_type="transcript",
            source_file="lesson.md",
            segment_id="T01-001",
        ),
        score=score,
    )


@pytest.mark.asyncio
async def test_write_answer_uses_llm_to_answer_question_from_context():
    writer = CurrentDocumentWriter(
        Settings(ai_provider="openrouter", ai_model="test-model", ai_api_key="test-key")
    )
    writer._client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="LLM trả lời trực tiếp"))]
                )
            )
        )
    )

    answer = await writer.write_answer(
        question="ReAct là gì?",
        hits=[make_hit("ReAct gồm Thought, Action và Observation.")],
    )

    assert answer == "LLM trả lời trực tiếp"


def test_context_ignores_low_scoring_hits():
    context = CurrentDocumentWriter.build_answer_context(
        [make_hit("Đoạn tốt", 0.8), make_hit("Đoạn nhiễu", 0.2)],
        minimum_score=0.5,
    )

    assert "Đoạn tốt" in context
    assert "Đoạn nhiễu" not in context
