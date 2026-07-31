import { FormEvent, useEffect, useState } from "react";

import { getConversation, getConversations, sendChat, uploadDocument } from "../services/api";
import type { ChatResponse, Citation, ConversationSummary, CurrentDocument, UploadResponse } from "../types/api";
import { CitationLink } from "./CitationLink";

type TutorChatProps = {
  learnerId: string;
  courseId: string;
  currentLessonId: string | null;
  onOpenCitation: (citation: Citation) => void;
  currentDocument?: CurrentDocument;
};

type ChatTurn = {
  role: "assistant" | "user";
  content: string;
  response?: ChatResponse;
};

export function TutorChat({ learnerId, courseId, currentLessonId, onOpenCitation, currentDocument }: TutorChatProps) {
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
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
  }, [currentLessonId]);

  async function refreshHistory() {
    try {
      setConversations(await getConversations(learnerId, courseId));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Không tải được lịch sử chat");
    }
  }

  useEffect(() => {
    void refreshHistory();
  }, [learnerId, courseId]);

  function startNewConversation() {
    setConversationId(null);
    setChatTurns([{ role: "assistant", content: "Hỏi mình về lesson, khái niệm, bài giảng, hoặc upload tài liệu riêng để đối chiếu." }]);
    setIsHistoryOpen(false);
  }

  async function openConversation(id: string) {
    try {
      const conversation = await getConversation(id, learnerId, courseId);
      setConversationId(conversation.conversation_id);
      setChatTurns(conversation.messages.map((item) => ({
        role: item.role,
        content: item.content,
        response: item.role === "assistant"
          ? { conversation_id: conversation.conversation_id, answer: item.content, citations: item.citations, confidence: "medium", needs_clarification: false, suggested_next_action: null }
          : undefined,
      })));
      setIsHistoryOpen(false);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Không mở được lịch sử chat");
    }
  }

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
        current_document: currentDocument,
        uploaded_document_ids: uploads.map((upload) => upload.document_id),
        conversation_id: conversationId ?? undefined,
      });
      setConversationId(response.conversation_id);
      setChatTurns((current) => [
        ...current,
        { role: "assistant", content: response.answer, response },
      ]);
      void refreshHistory();
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
        <div className="chat-title-row"><h2>Cross-Lesson Chat</h2><button className="history-toggle" type="button" onClick={() => setIsHistoryOpen((value) => !value)}>Lịch sử</button></div>
      </header>

      {isHistoryOpen ? <section className="history-panel">
        <button className="new-chat-button" type="button" onClick={startNewConversation}>+ Cuộc trò chuyện mới</button>
        {conversations.length ? conversations.map((conversation) => <button key={conversation.conversation_id} className={`history-item ${conversation.conversation_id === conversationId ? "is-active" : ""}`} type="button" onClick={() => void openConversation(conversation.conversation_id)}>{conversation.title}</button>) : <p className="history-empty">Chưa có cuộc hội thoại nào.</p>}
      </section> : null}

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
                    onOpen={onOpenCitation}
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
