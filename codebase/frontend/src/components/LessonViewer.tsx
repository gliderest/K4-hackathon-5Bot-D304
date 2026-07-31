import type { LessonDetailResponse } from "../types/api";

type LessonViewerProps = {
  lesson: LessonDetailResponse | null;
};

export function LessonViewer({ lesson }: LessonViewerProps) {
  if (!lesson) {
    return <div className="viewer-empty">Đang tải nội dung lesson...</div>;
  }

  return (
    <>
      <header className="viewer-header">
        <p className="eyebrow">Lesson Viewer</p>
        <h2>{lesson.title}</h2>
        <a href={lesson.transcript_viewer_path} target="_blank" rel="noreferrer">
          Mở transcript gốc
        </a>
      </header>

      {lesson.slide_viewer_path ? (
        <div className="slide-frame">
          <iframe
            key={lesson.slide_viewer_path}
            src={lesson.slide_viewer_path}
            title={`${lesson.title} slides`}
          />
        </div>
      ) : (
        <div className="viewer-empty">Lesson này chưa gắn file slide.</div>
      )}

    </>
  );
}
