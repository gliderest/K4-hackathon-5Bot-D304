from backend.app.agent.request_router import ToolRoute, choose_tool_route, is_greeting
from backend.app.schemas.chat import CurrentDocument


def test_common_greeting_is_not_treated_as_knowledge_question():
    assert is_greeting("chào bạn") is True
    assert is_greeting("Xin chào") is True


def test_normal_question_is_not_greeting():
    assert is_greeting("Machine learning là gì?") is False


def test_question_about_currently_open_slide_uses_current_document():
    document = CurrentDocument(
        source_type="slide",
        source_id="d2-slide-hackathon.pdf",
        title="Xác định bài toán cho AI",
    )

    assert choose_tool_route("Bạn có thể đọc được slide đang được mở không?", document) is ToolRoute.ANALYSE_CURRENT_DOCUMENT
