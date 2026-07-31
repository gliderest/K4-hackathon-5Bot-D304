import type { CourseLesson, ProgressSnapshot } from "../types/api";

type LessonCatalogProps = {
  lessons: CourseLesson[];
  progress: ProgressSnapshot | null;
  selectedLessonId: string | null;
  onSelectLesson: (lessonId: string) => void;
};

export function LessonCatalog({
  lessons,
  progress,
  selectedLessonId,
  onSelectLesson,
}: LessonCatalogProps) {
  const weakTopics = progress?.weak_topics ?? [];

  return (
    <>
      <header className="catalog-header">
        <p className="eyebrow">Learning Map</p>
        <h1>VLearn Course Outline</h1>
        <p>Chọn lesson để xem transcript, slide và tiếp tục hỏi AI tutor.</p>
      </header>

      <section className="lesson-list">
        {lessons.map((lesson) => {
          const isSelected = lesson.lesson_id === selectedLessonId;
          return (
            <button
              key={lesson.lesson_id}
              className={`lesson-card ${isSelected ? "is-selected" : ""}`}
              onClick={() => onSelectLesson(lesson.lesson_id)}
              type="button"
            >
              <span className="lesson-card-top">
                <strong>{lesson.lesson_id}</strong>
                <span>{lesson.completion_percent}%</span>
              </span>
              <span className="lesson-title">{lesson.title}</span>
              <span className="lesson-meta">{lesson.segment_count} đoạn transcript</span>
            </button>
          );
        })}
      </section>

      <section className="memory-panel">
        <h2>Memory</h2>
        <p>Weak topics</p>
        <div className="tag-wrap">
          {weakTopics.length ? weakTopics.map((topic) => <span key={topic} className="tag">{topic}</span>) : <span className="tag muted">Chưa có</span>}
        </div>
      </section>
    </>
  );
}
