import { useState } from "react";

import {
  cancelAdditionalDocument,
  confirmAdditionalDocument,
  stageAdditionalDocument,
} from "../services/api";
import type {
  AdditionalDocument,
  CourseLesson,
  CourseSlide,
  ProgressSnapshot,
  StagedAdditionalDocument,
} from "../types/api";

type LessonCatalogProps = {
  lessons: CourseLesson[];
  slides: CourseSlide[];
  additionalDocuments: AdditionalDocument[];
  progress: ProgressSnapshot | null;
  selectedLessonId: string | null;
  selectedSlideId: string | null;
  selectedAdditionalDocumentId: string | null;
  onSelectLesson: (lessonId: string) => void;
  onSelectSlide: (slide: CourseSlide) => void;
  onSelectAdditionalDocument: (document: AdditionalDocument) => void;
  onAdditionalDocumentsChanged: () => void;
};

export function LessonCatalog({
  lessons,
  slides,
  additionalDocuments,
  progress,
  selectedLessonId,
  selectedSlideId,
  selectedAdditionalDocumentId,
  onSelectLesson,
  onSelectSlide,
  onSelectAdditionalDocument,
  onAdditionalDocumentsChanged,
}: LessonCatalogProps) {
  const weakTopics = progress?.weak_topics ?? [];
  const [stagedDocument, setStagedDocument] = useState<StagedAdditionalDocument | null>(null);
  const [isSavingDocument, setIsSavingDocument] = useState(false);
  const [documentError, setDocumentError] = useState<string | null>(null);
  const isScriptGroupActive = Boolean(selectedLessonId);
  const isSlideGroupActive = Boolean(selectedSlideId);
  const isAdditionalGroupActive = Boolean(selectedAdditionalDocumentId || stagedDocument);

  async function handleStageDocument(file: File | null) {
    if (!file) return;
    setDocumentError(null);
    try {
      if (stagedDocument) await cancelAdditionalDocument(stagedDocument.stage_id);
      setStagedDocument(await stageAdditionalDocument(file));
    } catch (caught) {
      setDocumentError(caught instanceof Error ? caught.message : "Không tải được tài liệu");
    }
  }

  async function saveStagedDocument() {
    if (!stagedDocument) return;
    setIsSavingDocument(true);
    setDocumentError(null);
    try {
      await confirmAdditionalDocument(stagedDocument.stage_id);
      setStagedDocument(null);
      onAdditionalDocumentsChanged();
    } catch (caught) {
      setDocumentError(caught instanceof Error ? caught.message : "Không lưu được tài liệu");
    } finally {
      setIsSavingDocument(false);
    }
  }

  async function cancelStagedDocument() {
    if (!stagedDocument) return;
    try {
      await cancelAdditionalDocument(stagedDocument.stage_id);
    } finally {
      setStagedDocument(null);
    }
  }

  return (
    <>
      <header className="catalog-header">
        <p className="eyebrow">Learning Map</p>
        <h1>VLearn Course Outline</h1>
        <p>Chọn Script, Slide hoặc tài liệu thêm để xem nội dung và hỏi AI Tutor.</p>
      </header>

      <section className="catalog-content" aria-label="Danh mục tài liệu khóa học">
        <div className="catalog-group">
          <div className={`catalog-source-frame ${isScriptGroupActive ? "is-active" : ""}`} tabIndex={0}>
            <div className="catalog-group-heading">
              <h2 className="catalog-group-title">Script bài giảng</h2>
              <span className="catalog-group-count">{lessons.length}</span>
            </div>
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
          <div className={`catalog-source-frame ${isSlideGroupActive ? "is-active" : ""}`} tabIndex={0}>
            <div className="catalog-group-heading">
              <h2 className="catalog-group-title">Slides</h2>
              <span className="catalog-group-count">{slides.length}</span>
            </div>
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
          <div className={`catalog-source-frame ${isAdditionalGroupActive ? "is-active" : ""}`} tabIndex={0}>
            <div className="additional-document-heading">
              <div className="catalog-group-heading">
                <h2 className="catalog-group-title">Tài liệu thêm</h2>
                <span className="catalog-group-count">{additionalDocuments.length}</span>
              </div>
              <label className="add-document-button">Thêm tài liệu<input type="file" accept=".pdf,.docx,.txt,.md" onChange={(event) => void handleStageDocument(event.target.files?.[0] ?? null)} /></label>
            </div>
            {stagedDocument ? <div className="staged-document-chip"><span>📎 {stagedDocument.file_name}</span><span className="staged-document-actions"><button type="button" onClick={() => void saveStagedDocument()} disabled={isSavingDocument}>{isSavingDocument ? "Đang lưu" : "Lưu"}</button><button type="button" onClick={() => void cancelStagedDocument()} disabled={isSavingDocument}>Hủy</button></span></div> : null}
            {documentError ? <p className="document-error">{documentError}</p> : null}
            <div className="lesson-list additional-document-list">
              {additionalDocuments.length ? additionalDocuments.map((document) => (
                <button key={document.document_id} className={`lesson-card ${document.document_id === selectedAdditionalDocumentId ? "is-selected" : ""}`} onClick={() => onSelectAdditionalDocument(document)} type="button"><span className="lesson-title">{document.title}</span><span className="lesson-meta">{document.file_name}</span></button>
              )) : <p className="history-empty">Chưa có tài liệu dùng chung.</p>}
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
