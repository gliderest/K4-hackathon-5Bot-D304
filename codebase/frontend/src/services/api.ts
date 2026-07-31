import type {
  ChatRequest,
  ChatResponse,
  AdditionalDocument,
  CourseOutlineResponse,
  ConversationDetail,
  ConversationSummary,
  LessonDetailResponse,
  ProgressSnapshot,
  UploadResponse,
  StagedAdditionalDocument,
  ToolTraceEvent,
} from "../types/api";

const API_ROOT = "/api";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_ROOT}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  return parseJson<ChatResponse>(response);
}

export async function sendChatStream(
  request: ChatRequest,
  onTrace: (event: ToolTraceEvent) => void,
): Promise<ChatResponse> {
  const response = await fetch(`${API_ROOT}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  if (!response.body) throw new Error("Trình duyệt không hỗ trợ luồng phản hồi chat");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const consumeEvent = (rawEvent: string): ChatResponse | null => {
    const lines = rawEvent.split("\n");
    const eventName = lines.find((line) => line.startsWith("event:"))?.slice(6).trim();
    const data = lines
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trim())
      .join("\n");
    if (!eventName || !data) return null;
    const payload = JSON.parse(data) as ToolTraceEvent | ChatResponse | { detail?: string };
    if (eventName === "tool_trace") {
      onTrace(payload as ToolTraceEvent);
      return null;
    }
    if (eventName === "answer") return payload as ChatResponse;
    if (eventName === "error") {
      throw new Error((payload as { detail?: string }).detail || "Không thể tạo câu trả lời");
    }
    return null;
  };

  while (true) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value, { stream: !done }).replace(/\r\n/g, "\n");
    let boundary = buffer.indexOf("\n\n");
    while (boundary >= 0) {
      const answer = consumeEvent(buffer.slice(0, boundary));
      buffer = buffer.slice(boundary + 2);
      if (answer) return answer;
      boundary = buffer.indexOf("\n\n");
    }
    if (done) break;
  }
  throw new Error("Luồng phản hồi chat kết thúc trước khi có câu trả lời");
}

export async function getConversations(
  learnerId: string,
  courseId: string,
): Promise<ConversationSummary[]> {
  const response = await fetch(
    `${API_ROOT}/chat/history?learner_id=${encodeURIComponent(learnerId)}&course_id=${encodeURIComponent(courseId)}`,
  );
  return parseJson<ConversationSummary[]>(response);
}

export async function getConversation(
  conversationId: string,
  learnerId: string,
  courseId: string,
): Promise<ConversationDetail> {
  const response = await fetch(
    `${API_ROOT}/chat/history/${encodeURIComponent(conversationId)}?learner_id=${encodeURIComponent(learnerId)}&course_id=${encodeURIComponent(courseId)}`,
  );
  return parseJson<ConversationDetail>(response);
}

export async function getOutline(
  courseId: string,
  learnerId: string,
): Promise<CourseOutlineResponse> {
  const response = await fetch(
    `${API_ROOT}/courses/${courseId}/outline?learner_id=${encodeURIComponent(learnerId)}`,
  );
  return parseJson<CourseOutlineResponse>(response);
}

export async function getLesson(
  courseId: string,
  lessonId: string,
): Promise<LessonDetailResponse> {
  const response = await fetch(`${API_ROOT}/courses/${courseId}/lessons/${lessonId}`);
  return parseJson<LessonDetailResponse>(response);
}

export async function getProgress(
  learnerId: string,
  courseId: string,
): Promise<ProgressSnapshot> {
  const response = await fetch(
    `${API_ROOT}/progress/${learnerId}?course_id=${encodeURIComponent(courseId)}`,
  );
  return parseJson<ProgressSnapshot>(response);
}

export async function uploadDocument(
  learnerId: string,
  conversationId: string,
  file: File,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.set("learner_id", learnerId);
  formData.set("conversation_id", conversationId);
  formData.set("file", file);

  const response = await fetch(`${API_ROOT}/uploads`, {
    method: "POST",
    body: formData,
  });
  return parseJson<UploadResponse>(response);
}

export async function stageAdditionalDocument(file: File): Promise<StagedAdditionalDocument> {
  const formData = new FormData();
  formData.set("file", file);
  const response = await fetch(`${API_ROOT}/additional-documents/stage`, { method: "POST", body: formData });
  return parseJson<StagedAdditionalDocument>(response);
}

export async function confirmAdditionalDocument(stageId: string): Promise<AdditionalDocument> {
  const response = await fetch(`${API_ROOT}/additional-documents/${encodeURIComponent(stageId)}/confirm`, { method: "POST" });
  return parseJson<AdditionalDocument>(response);
}

export async function cancelAdditionalDocument(stageId: string): Promise<void> {
  const response = await fetch(`${API_ROOT}/additional-documents/${encodeURIComponent(stageId)}`, { method: "DELETE" });
  if (!response.ok) throw new Error((await response.text()) || "Không hủy được bản nháp tài liệu");
}
