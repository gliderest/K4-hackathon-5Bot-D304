import type { CourseLesson, CourseSlide, ProgressSnapshot } from "../types/api";

type LessonCatalogProps = {
  lessons: CourseLesson[];
  slides: CourseSlide[];
  progress: ProgressSnapshot | null;
  selectedLessonId: string | null;
  selectedSlideId: string | null;
  onSelectLesson: (lessonId: string) => void;
  onSelectSlide: (slide: CourseSlide) => void;
};

export function LessonCatalog({
  lessons,
  slides,
  progress,
  selectedLessonId,
  selectedSlideId,
  onSelectLesson,
  onSelectSlide,
}: LessonCatalogProps) {
  const weakTopics = progress?.weak_topics ?? [];

  return (
    <>
      <header className="catalog-header">
        <p className="eyebrow">Learning Map</p>
        <h1>VLearn Course Outline</h1>
        <p>Chọn Script hoặc Slide để xem tài liệu và tiếp tục hỏi AI Tutor.</p>
      </header>

      <section className="catalog-content" aria-label="Danh mục tài liệu khóa học">
        <div className="catalog-group">
          <div className="catalog-source-frame">
            <h2 className="catalog-group-title">Script bài giảng</h2>
            <div className="lesson-list">
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
                <strong>Script {lesson.lesson_id.replace("lesson-", "")}</strong>
                <span>{lesson.completion_percent}%</span>
              </span>
              <span className="lesson-title">{lesson.title}</span>
              <span className="lesson-meta">{lesson.segment_count} đoạn transcript</span>
            </button>
          );
            })}
            </div>
          </div>
        </div>
        <div className="catalog-group">
          <div className="catalog-source-frame">
            <h2 className="catalog-group-title">Slide</h2>
            <div className="lesson-list slide-list">
            {slides.map((slide) => (
              <button key={slide.slide_id} className={`lesson-card ${slide.slide_id === selectedSlideId ? "is-selected" : ""}`} onClick={() => onSelectSlide(slide)} type="button">
                <span className="lesson-card-top"><strong>Slide</strong></span>
                <span className="lesson-title">{slide.title}</span>
                <span className="lesson-meta">{slide.slide_file}</span>
              </button>
            ))}
            </div>
          </div>
        </div>
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
