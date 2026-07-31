import { useEffect } from "react";

import type { LessonDetailResponse } from "../types/api";

type LessonViewerProps = {
  content: ViewerContent | null;
};

export type ViewerContent =
  | { type: "script"; lesson: LessonDetailResponse; segmentId?: string | null }
  | { type: "slide"; slideId: string; title: string; viewerPath: string }
  | { type: "document"; title: string; viewerPath: string };

export function LessonViewer({ content }: LessonViewerProps) {
  useEffect(() => {
    if (content?.type !== "script" || !content.segmentId) return;
    document.getElementById(`transcript-segment-${content.segmentId}`)?.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  }, [content]);

  if (!content) {
    return <div className="viewer-empty">Đang tải nội dung lesson...</div>;
  }

  if (content.type === "script") {
    const { lesson } = content;
    return <>
      <header className="viewer-header"><p className="eyebrow">Script bài giảng</p><h2>{lesson.title}</h2><a href={lesson.transcript_viewer_path} target="_blank" rel="noreferrer">Mở file transcript gốc</a></header>
      <article className="script-viewer full-height" aria-label={`Nội dung ${lesson.title}`}>
        {lesson.transcript_markdown.split("\n").map((line, index) => {
          const segmentMatch = line.match(/^\*\*\[([^\]]+)\]\*/);
          const segmentId = segmentMatch?.[1];
          return line ? (
            <p
              key={`${segmentId ?? "line"}-${index}`}
              id={segmentId ? `transcript-segment-${segmentId}` : undefined}
              className={segmentId === content.segmentId ? "transcript-line is-target" : "transcript-line"}
            >
              {line}
            </p>
          ) : <br key={`break-${index}`} />;
        })}
      </article>
    </>;
  }

  if (content.type === "document") {
    return <>
      <header className="viewer-header"><p className="eyebrow">Tài liệu tham chiếu</p><h2>{content.title}</h2></header>
      <div className="slide-frame"><iframe key={content.viewerPath} src={content.viewerPath} title={content.title} /></div>
    </>;
  }

  return <>
    <header className="viewer-header"><p className="eyebrow">Slide bài giảng</p><h2>{content.title}</h2></header>
    <div className="slide-frame"><iframe key={content.viewerPath} src={content.viewerPath} title={`${content.title} slides`} /></div>
  </>;
}
