import { useEffect, useState } from "react";

import { LessonCatalog } from "./components/LessonCatalog";
import { LessonViewer } from "./components/LessonViewer";
import type { ViewerContent } from "./components/LessonViewer";
import { TutorChat } from "./components/TutorChat";
import { getLesson, getOutline, getProgress } from "./services/api";
import type {
  CourseOutlineResponse,
  AdditionalDocument,
  CourseSlide,
  Citation,
  CurrentDocument,
  LessonDetailResponse,
  ProgressSnapshot,
} from "./types/api";

const LEARNER_ID = "demo-learner";
const COURSE_ID = "vlearn-hackathon";

export default function App() {
  const [outline, setOutline] = useState<CourseOutlineResponse | null>(null);
  const [progress, setProgress] = useState<ProgressSnapshot | null>(null);
  const [selectedLessonId, setSelectedLessonId] = useState<string | null>(null);
  const [selectedSlideId, setSelectedSlideId] = useState<string | null>(null);
  const [selectedAdditionalDocument, setSelectedAdditionalDocument] = useState<AdditionalDocument | null>(null);
  const [selectedLesson, setSelectedLesson] = useState<LessonDetailResponse | null>(null);
  const [selectedTranscriptSegmentId, setSelectedTranscriptSegmentId] = useState<string | null>(null);
  const [selectedSlideViewerPath, setSelectedSlideViewerPath] = useState<string | null>(null);
  const [selectedExternalCitation, setSelectedExternalCitation] = useState<Citation | null>(null);
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

  function selectScript(lessonId: string) {
    setSelectedAdditionalDocument(null);
    setSelectedExternalCitation(null);
    setSelectedSlideId(null);
    setSelectedSlideViewerPath(null);
    setSelectedTranscriptSegmentId(null);
    setSelectedLesson(null);
    setSelectedLessonId(lessonId);
  }

  function selectSlide(slide: CourseSlide) {
    setSelectedAdditionalDocument(null);
    setSelectedExternalCitation(null);
    setSelectedLessonId(null);
    setSelectedLesson(null);
    setSelectedTranscriptSegmentId(null);
    setSelectedSlideViewerPath(null);
    setSelectedSlideId(slide.slide_id);
  }

  function selectAdditionalDocument(document: AdditionalDocument) {
    setSelectedLessonId(null);
    setSelectedLesson(null);
    setSelectedSlideId(null);
    setSelectedSlideViewerPath(null);
    setSelectedTranscriptSegmentId(null);
    setSelectedExternalCitation(null);
    setSelectedAdditionalDocument(document);
  }

  async function refreshOutline() {
    try {
      setOutline(await getOutline(COURSE_ID, LEARNER_ID));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Không tải được tài liệu thêm");
    }
  }

  function openCitation(citation: Citation) {
    if (citation.source_type === "slide") {
      const slide = outline?.slides.find((item) => item.slide_file === citation.source_id);
      if (!slide) return;
      setSelectedLessonId(null);
      setSelectedExternalCitation(null);
      setSelectedLesson(null);
      setSelectedTranscriptSegmentId(null);
      setSelectedSlideId(slide.slide_id);
      setSelectedSlideViewerPath(citation.viewer_path);
      return;
    }

    if (citation.source_type === "transcript" && citation.lesson_id) {
      setSelectedSlideId(null);
      setSelectedExternalCitation(null);
      setSelectedSlideViewerPath(null);
      setSelectedLesson(null);
      setSelectedTranscriptSegmentId(citation.segment_id);
      setSelectedLessonId(citation.lesson_id);
      return;
    }

    setSelectedLessonId(null);
    setSelectedLesson(null);
    setSelectedSlideId(null);
    setSelectedSlideViewerPath(null);
    setSelectedTranscriptSegmentId(null);
    setSelectedExternalCitation(citation);
  }

  const selectedSlide = outline?.slides.find((slide) => slide.slide_id === selectedSlideId);
  const currentDocument: CurrentDocument | undefined = selectedExternalCitation
    ? {
        source_type: selectedExternalCitation.source_type,
        source_id: selectedExternalCitation.source_id,
        title: selectedExternalCitation.label,
        lesson_id: selectedExternalCitation.lesson_id,
      }
    : selectedLesson
      ? {
          source_type: "transcript",
          source_id: selectedLesson.transcript_file,
          title: selectedLesson.title,
          lesson_id: selectedLesson.lesson_id,
        }
      : selectedSlide
        ? {
            source_type: "slide",
            source_id: selectedSlide.slide_file,
            title: selectedSlide.title,
          }
        : undefined;
  const viewerContent: ViewerContent | null = selectedExternalCitation
    ? { type: "document", title: selectedExternalCitation.label, viewerPath: selectedExternalCitation.viewer_path }
    : selectedAdditionalDocument
      ? { type: "document", title: selectedAdditionalDocument.title, viewerPath: selectedAdditionalDocument.viewer_path }
    : selectedLesson
    ? { type: "script", lesson: selectedLesson, segmentId: selectedTranscriptSegmentId }
    : selectedSlide
      ? { type: "slide", slideId: selectedSlide.slide_id, title: selectedSlide.title, viewerPath: selectedSlideViewerPath ?? selectedSlide.slide_viewer_path }
      : null;

  return (
    <main className={`three-pane-layout ${isChatOpen ? "" : "chat-is-hidden"}`}>
      <aside className="pane catalog-pane">
        <LessonCatalog
          lessons={outline?.lessons ?? []}
          slides={outline?.slides ?? []}
          additionalDocuments={outline?.additional_documents ?? []}
          progress={progress}
          selectedLessonId={selectedLessonId}
          selectedSlideId={selectedSlideId}
          selectedAdditionalDocumentId={selectedAdditionalDocument?.document_id ?? null}
          onSelectLesson={selectScript}
          onSelectSlide={selectSlide}
          onSelectAdditionalDocument={selectAdditionalDocument}
          onAdditionalDocumentsChanged={() => void refreshOutline()}
        />
      </aside>

      <section className="pane viewer-pane">
        {error ? <p className="error-text">{error}</p> : null}
        <LessonViewer content={viewerContent} />
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
            onOpenCitation={openCitation}
            currentDocument={currentDocument}
          />
        </aside>
      ) : null}
    </main>
  );
}
