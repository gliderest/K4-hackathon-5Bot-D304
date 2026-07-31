import { FormEvent, useEffect, useState } from "react";

import { sendChat, uploadDocument } from "../services/api";
import type { ChatResponse, UploadResponse } from "../types/api";
import { CitationLink } from "./CitationLink";

type TutorChatProps = {
  learnerId: string;
  courseId: string;
  currentLessonId: string | null;
};

type ChatTurn = {
  role: "assistant" | "user";
  content: string;
  response?: ChatResponse;
};

export function TutorChat({ learnerId, courseId, currentLessonId }: TutorChatProps) {
  const [message, setMessage] = useState("");
  const [chatTurns, setChatTurns] = useState<ChatTurn[]>([
    {
      role: "assistant",
      content:
        "Hỏi mình về lesson, khái niệm, bài giảng, hoặc upload tài liệu riêng để đối chiếu.",
    },
  ]);
  const [isSending, setIsSending] = useState(false);
  const [uploads, setUploads] = useState<UploadResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
  }, [currentLessonId]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim()) return;

    const nextMessage = message.trim();
    setChatTurns((current) => [...current, { role: "user", content: nextMessage }]);
    setMessage("");
    setIsSending(true);
    setError(null);

    try {
      const response = await sendChat({
        learner_id: learnerId,
        course_id: courseId,
        message: nextMessage,
        current_lesson_id: currentLessonId ?? undefined,
        uploaded_document_ids: uploads.map((upload) => upload.document_id),
      });
      setChatTurns((current) => [
        ...current,
        { role: "assistant", content: response.answer, response },
      ]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Không gửi được câu hỏi");
    } finally {
      setIsSending(false);
    }
  }

  async function handleUpload(file: File | null) {
    if (!file) return;
    setError(null);
    try {
      const response = await uploadDocument(learnerId, file);
      setUploads((current) => [...current, response]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Không upload được file");
    }
  }

  return (
    <>
      <header className="chat-header">
        <p className="eyebrow">AI Tutor</p>
        <h2>Cross-Lesson Chat</h2>
      </header>

      <section className="chat-messages">
        {chatTurns.map((turn, index) => (
          <article key={`${turn.role}-${index}`} className={`message-card ${turn.role}`}>
            <strong>{turn.role === "assistant" ? "Tutor" : "Bạn"}</strong>
            <pre>{turn.content}</pre>
            {turn.response?.citations?.length ? (
              <div className="citation-stack">
                {turn.response.citations.map((citation) => (
                  <CitationLink
                    key={`${citation.source_id}-${citation.segment_id}-${citation.page}`}
                    citation={citation}
                  />
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </section>

      {uploads.length ? (
        <section className="upload-list">
          {uploads.map((upload) => (
            <a
              key={upload.document_id}
              className="upload-item"
              href={upload.viewer_path}
              target="_blank"
              rel="noreferrer"
            >
              {upload.file_name} ({upload.chunk_count} chunks)
            </a>
          ))}
        </section>
      ) : null}

      <form className="chat-composer" onSubmit={handleSubmit}>
        <div className="composer-box">
          <label className="upload-icon-button" title="Upload tài liệu">
            <span aria-hidden="true">+</span>
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md"
              onChange={(event) => handleUpload(event.target.files?.[0] ?? null)}
            />
          </label>

          <textarea
            aria-label="Câu hỏi"
            placeholder="Hỏi về lesson, slide, transcript..."
            value={message}
            onChange={(event) => setMessage(event.target.value)}
          />

          <button className="send-icon-button" type="submit" disabled={isSending} title="Gửi câu hỏi">
            <span aria-hidden="true">{isSending ? "..." : "↑"}</span>
          </button>
        </div>
      </form>

      {error ? <p className="error-text">{error}</p> : null}
    </>
  );
}
