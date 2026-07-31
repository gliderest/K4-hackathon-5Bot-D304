import type {
  CourseLesson,
  CourseSlide,
  UploadResponse,
} from "../types/api";

type LessonCatalogProps = {
  lessons: CourseLesson[];
  slides: CourseSlide[];
  uploadHistory: UploadResponse[];
  selectedLessonId: string | null;
  selectedSlideId: string | null;
  selectedUploadId: string | null;
  onSelectLesson: (lessonId: string) => void;
  onSelectSlide: (slide: CourseSlide) => void;
  onSelectUpload: (document: UploadResponse) => void;
};

export function LessonCatalog({
  lessons,
  slides,
  uploadHistory,
  selectedLessonId,
  selectedSlideId,
  selectedUploadId,
  onSelectLesson,
  onSelectSlide,
  onSelectUpload,
}: LessonCatalogProps) {
  return (
    <>
      <header className="catalog-header">
        <p className="eyebrow">Learning Map</p>
        <h1>VLearn Course Outline</h1>
        <p>Chọn Script hoặc Slide để xem nội dung. Tài liệu cá nhân được thêm trực tiếp trong khung chat.</p>
      </header>

      <section className="catalog-content" aria-label="Danh mục tài liệu khóa học">
        <div className="catalog-group">
          <div className="catalog-source-frame">
            <h2 className="catalog-group-title">Script bài giảng</h2>
            <div className="lesson-list">
              {lessons.map((lesson) => (
                <button key={lesson.lesson_id} className={`lesson-card ${lesson.lesson_id === selectedLessonId ? "is-selected" : ""}`} onClick={() => onSelectLesson(lesson.lesson_id)} type="button">
                  <span className="lesson-card-top"><strong>Script {lesson.lesson_id.replace("lesson-", "")}</strong><span>{lesson.completion_percent}%</span></span>
                  <span className="lesson-title">{lesson.title}</span>
                  <span className="lesson-meta">{lesson.segment_count} đoạn transcript</span>
                </button>
              ))}
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

        <div className="catalog-group additional-documents-group">
          <div className="catalog-source-frame">
            <div className="additional-document-heading">
              <h2 className="catalog-group-title">Lịch sử upload</h2>
            </div>
            <div className="lesson-list additional-document-list">
              {uploadHistory.length ? uploadHistory.map((document) => (
                <button key={document.document_id} className={`lesson-card ${document.document_id === selectedUploadId ? "is-selected" : ""}`} onClick={() => onSelectUpload(document)} type="button"><span className="lesson-title">{document.file_name}</span><span className="lesson-meta">{document.chunk_count} đoạn · Mở từ chat</span></button>
              )) : <p className="history-empty">Chưa có file upload. Hãy thêm file trong khung chat.</p>}
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
