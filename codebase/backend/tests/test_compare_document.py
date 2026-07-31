from backend.app.agent.request_router import ToolRoute, choose_tool_route
from backend.app.schemas.chat import CurrentDocument


def test_compare_request_uses_compare_route_for_open_upload():
    document = CurrentDocument(
        source_type="user_upload",
        source_id="doc-1",
        title="Bài làm của tôi",
        lesson_id="user-upload",
    )

    assert choose_tool_route(
        "So sánh tài liệu này với kiến thức trong slide và chỉ ra điểm đúng sai",
        document,
    ) is ToolRoute.COMPARE_DOCUMENT_WITH_COURSE


def test_compare_route_is_not_selected_without_open_document():
    assert choose_tool_route(
        "So sánh tài liệu upload với kiến thức trong slide",
        None,
    ) is ToolRoute.SEARCH_DOCUMENT
