export type Citation = {
  label: string;
  source_type: "slide" | "transcript" | "user_upload";
  source_id: string;
  lesson_id: string | null;
  page: number | null;
  segment_id: string | null;
  viewer_path: string;
  score: number | null;
};

export type ChatRequest = {
  learner_id: string;
  course_id: string;
  message: string;
  current_lesson_id?: string;
  current_document?: CurrentDocument;
  uploaded_document_ids?: string[];
  conversation_id?: string;
};

export type CurrentDocument = {
  source_type: "slide" | "transcript" | "user_upload";
  source_id: string;
  title: string;
  lesson_id?: string | null;
};

export type ChatResponse = {
  conversation_id: string;
  answer: string;
  citations: Citation[];
  confidence: "high" | "medium" | "low";
  needs_clarification: boolean;
  suggested_next_action: string | null;
};

export type ConversationSummary = {
  conversation_id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ConversationMessage = {
  role: "user" | "assistant";
  content: string;
  citations: Citation[];
  created_at: string;
};

export type ConversationDetail = {
  conversation_id: string;
  title: string;
  messages: ConversationMessage[];
};

export type CourseLesson = {
  lesson_id: string;
  title: string;
  transcript_file: string;
  slide_file: string | null;
  slide_viewer_path: string | null;
  segment_count: number;
  completion_percent: number;
};

export type CourseSlide = {
  slide_id: string;
  title: string;
  slide_file: string;
  slide_viewer_path: string;
};

export type CourseOutlineResponse = {
  course_id: string;
  learner_id: string;
  lessons: CourseLesson[];
  slides: CourseSlide[];
};

export type LessonDetailResponse = {
  course_id: string;
  lesson_id: string;
  title: string;
  transcript_markdown: string;
  transcript_file: string;
  transcript_viewer_path: string;
  slide_file: string | null;
  slide_viewer_path: string | null;
};

export type UploadResponse = {
  learner_id: string;
  document_id: string;
  file_name: string;
  viewer_path: string;
  chunk_count: number;
};

export type ProgressLesson = {
  lesson_id: string;
  completion_percent: number;
  last_position: string | null;
  last_seen_at: string | null;
};

export type ProgressSnapshot = {
  learner_id: string;
  course_id: string;
  lessons: ProgressLesson[];
  weak_topics: string[];
  review_queue: string[];
};
