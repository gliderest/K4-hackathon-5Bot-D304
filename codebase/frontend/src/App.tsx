import { useEffect, useState } from "react";

import { LessonCatalog } from "./components/LessonCatalog";
import { LessonViewer } from "./components/LessonViewer";
import { TutorChat } from "./components/TutorChat";
import { getLesson, getOutline, getProgress } from "./services/api";
import type {
  CourseOutlineResponse,
  LessonDetailResponse,
  ProgressSnapshot,
} from "./types/api";

const LEARNER_ID = "demo-learner";
const COURSE_ID = "vlearn-hackathon";

export default function App() {
  const [outline, setOutline] = useState<CourseOutlineResponse | null>(null);
  const [progress, setProgress] = useState<ProgressSnapshot | null>(null);
  const [selectedLessonId, setSelectedLessonId] = useState<string | null>(null);
  const [selectedLesson, setSelectedLesson] = useState<LessonDetailResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      try {
        const [outlineResponse, progressResponse] = await Promise.all([
          getOutline(COURSE_ID, LEARNER_ID),
          getProgress(LEARNER_ID, COURSE_ID),
        ]);
        setOutline(outlineResponse);
        setProgress(progressResponse);
        const firstLessonId = outlineResponse.lessons[0]?.lesson_id ?? null;
        setSelectedLessonId(firstLessonId);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Không tải được dữ liệu khóa học");
      }
    }

    void bootstrap();
  }, []);

  useEffect(() => {
    if (!selectedLessonId) return;
    const lessonId = selectedLessonId;
    async function loadLesson() {
      try {
        const response = await getLesson(COURSE_ID, lessonId);
        setSelectedLesson(response);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Không tải được lesson");
      }
    }

    void loadLesson();
  }, [selectedLessonId]);

  return (
    <main className={`three-pane-layout ${isChatOpen ? "" : "chat-is-hidden"}`}>
      <aside className="pane catalog-pane">
        <LessonCatalog
          lessons={outline?.lessons ?? []}
          progress={progress}
          selectedLessonId={selectedLessonId}
          onSelectLesson={setSelectedLessonId}
        />
      </aside>

      <section className="pane viewer-pane">
        {error ? <p className="error-text">{error}</p> : null}
        <LessonViewer lesson={selectedLesson} />
      </section>

      <button
        className="chat-toggle-button"
        type="button"
        aria-label={isChatOpen ? "Ẩn khung chat" : "Hiện khung chat"}
        aria-expanded={isChatOpen}
        onClick={() => setIsChatOpen((current) => !current)}
        title={isChatOpen ? "Ẩn khung chat" : "Hiện khung chat"}
      >
        <span className="chat-toggle-icon" aria-hidden="true" />
      </button>

      {isChatOpen ? (
        <aside className="pane chat-pane">
          <TutorChat
            learnerId={LEARNER_ID}
            courseId={COURSE_ID}
            currentLessonId={selectedLessonId}
          />
        </aside>
      ) : null}
    </main>
  );
}
