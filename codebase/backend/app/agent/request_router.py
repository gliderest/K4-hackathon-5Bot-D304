"""Route a learner message to the narrowest document tool that can answer it."""

from enum import Enum

from backend.app.schemas.chat import CurrentDocument


class ToolRoute(str, Enum):
    ANALYSE_CURRENT_DOCUMENT = "analyse_current_document"
    SEARCH_DOCUMENT = "search_document"
    CLARIFY = "clarify"


SEARCH_SIGNALS = (
    "tìm",
    "tìm kiếm",
    "ở đâu",
    "nằm ở",
    "lesson nào",
    "bài nào",
    "file nào",
    "nguồn nào",
    "nguồn của",
    "toàn khóa",
    "toàn bộ tài liệu",
    "ngoài bài",
    "ngoài tài liệu",
    "so sánh các",
)
SUMMARY_SIGNALS = ("tóm tắt", "tổng hợp", "ý chính", "dàn ý")
CONTENT_CREATION_SIGNALS = (
    "trắc nghiệm",
    "quiz",
    "flashcard",
    "câu hỏi ôn tập",
    "tạo câu hỏi",
    "ra câu hỏi",
    "soạn câu hỏi",
    "tạo bài tập",
    "ra bài tập",
    "tạo đề",
)
CURRENT_DOCUMENT_SIGNALS = (
    "tài liệu này",
    "bài này",
    "slide này",
    "script này",
    "trang này",
    "nội dung này",
    "đoạn này",
)
ANALYSIS_SIGNALS = ("giải thích", "phân tích", "làm rõ", "diễn giải")


def choose_tool_route(message: str, current_document: CurrentDocument | None) -> ToolRoute:
    normalized = message.casefold().strip()
    if len(normalized) < 8:
        return ToolRoute.CLARIFY
    # Creation tasks use the open document as their only source. Check these
    # signals before search terms: "tạo quiz từ bài giảng" is not a request to
    # locate another lesson merely because it contains the word "bài".
    if any(signal in normalized for signal in CONTENT_CREATION_SIGNALS):
        return ToolRoute.ANALYSE_CURRENT_DOCUMENT
    if any(signal in normalized for signal in SUMMARY_SIGNALS):
        return ToolRoute.ANALYSE_CURRENT_DOCUMENT
    if current_document and any(signal in normalized for signal in CURRENT_DOCUMENT_SIGNALS):
        return ToolRoute.ANALYSE_CURRENT_DOCUMENT
    if current_document and any(signal in normalized for signal in ANALYSIS_SIGNALS):
        return ToolRoute.ANALYSE_CURRENT_DOCUMENT
    if any(signal in normalized for signal in SEARCH_SIGNALS):
        return ToolRoute.SEARCH_DOCUMENT
    return ToolRoute.SEARCH_DOCUMENT
