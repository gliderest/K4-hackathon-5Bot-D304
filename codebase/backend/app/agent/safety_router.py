"""Keep the tutor within its learning scope before any retrieval tool is used."""

from enum import Enum

from backend.app.schemas.chat import CurrentDocument


OUT_OF_SCOPE_RESPONSE = (
    "Tôi có nhiệm vụ hỗ trợ bạn học tập, chủ đề của bạn nằm ngoài phạm vi của tôi"
)


class MessageScope(str, Enum):
    LEARNING = "learning"
    OUT_OF_SCOPE = "out_of_scope"
    PROMPT_INJECTION = "prompt_injection"


# These patterns indicate an attempt to override, inspect, or damage the system.
# They are intentionally evaluated before learning-topic signals.
PROMPT_INJECTION_SIGNALS = (
    "ignore previous instructions",
    "ignore all instructions",
    "bỏ qua hướng dẫn",
    "bo qua huong dan",
    "bỏ qua chỉ dẫn",
    "bo qua chi dan",
    "system prompt",
    "prompt hệ thống",
    "prompt he thong",
    "developer message",
    "jailbreak",
    "dan mode",
    "override system",
    "vượt qua system prompt",
    "vuot qua system prompt",
    "phá hoại hệ thống",
    "pha hoai he thong",
    "hack hệ thống",
    "hack he thong",
    "tiết lộ prompt",
    "tiet lo prompt",
    "reveal your prompt",
)
SECRET_SIGNALS = ("api key", "api_key", "secret key", "mật khẩu", "mat khau", "access token")
SECRET_ACTIONS = ("tiết lộ", "tiet lo", "hiển thị", "hien thi", "in ra", "trích xuất", "trich xuat", "lấy ", "lay ")
DESTRUCTIVE_ACTIONS = ("xóa", "xoa", "delete", "format", "rm -rf", "drop table")
SYSTEM_TARGETS = ("database", "cơ sở dữ liệu", "co so du lieu", "hệ thống", "he thong", "server", "tệp", "file")

# This tutor is for the AI Thực Chiến course. A current learning document also
# establishes scope for transformations such as summaries and quizzes.
COURSE_TOPIC_SIGNALS = (
    "trí tuệ nhân tạo",
    "tri tue nhan tao",
    "machine learning",
    "học máy",
    "hoc may",
    "llm",
    "rag",
    "chatbot",
    "prompt",
    "embedding",
    "vector",
    "dữ liệu",
    "du lieu",
    "mô hình",
    "mo hinh",
    "model",
    "api",
    "automation",
    "bài giảng",
    "bai giang",
    "lesson",
    "slide",
    "script",
    "transcript",
    "học liệu",
    "hoc lieu",
    "khóa học",
    "khoa hoc",
)
DOCUMENT_ACTION_SIGNALS = (
    "tóm tắt",
    "tom tat",
    "giải thích",
    "giai thich",
    "phân tích",
    "phan tich",
    "trắc nghiệm",
    "trac nghiem",
    "quiz",
    "flashcard",
    "bài tập",
    "bai tap",
)


def classify_message_scope(
    message: str,
    current_document: CurrentDocument | None,
) -> MessageScope:
    normalized = message.casefold().strip()

    if any(signal in normalized for signal in PROMPT_INJECTION_SIGNALS):
        return MessageScope.PROMPT_INJECTION
    if (
        any(signal in normalized for signal in SECRET_SIGNALS)
        and any(action in normalized for action in SECRET_ACTIONS)
    ):
        return MessageScope.PROMPT_INJECTION
    if (
        any(action in normalized for action in DESTRUCTIVE_ACTIONS)
        and any(target in normalized for target in SYSTEM_TARGETS)
    ):
        return MessageScope.PROMPT_INJECTION

    if current_document and any(signal in normalized for signal in DOCUMENT_ACTION_SIGNALS):
        return MessageScope.LEARNING
    # Keep uppercase AI distinct from the Vietnamese pronoun "ai" so questions
    # such as "ai là..." do not accidentally pass the course-scope gate.
    if "AI" in message:
        return MessageScope.LEARNING
    if any(signal in normalized for signal in COURSE_TOPIC_SIGNALS):
        return MessageScope.LEARNING
    return MessageScope.OUT_OF_SCOPE
