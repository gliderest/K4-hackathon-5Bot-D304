import type {
  ChatRequest,
  ChatResponse,
  CourseOutlineResponse,
  LessonDetailResponse,
  ProgressSnapshot,
  UploadResponse,
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
  file: File,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.set("learner_id", learnerId);
  formData.set("file", file);

  const response = await fetch(`${API_ROOT}/uploads`, {
    method: "POST",
    body: formData,
  });
  return parseJson<UploadResponse>(response);
}
