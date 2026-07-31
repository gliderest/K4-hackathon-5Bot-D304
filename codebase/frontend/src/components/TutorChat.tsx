import { FormEvent, KeyboardEvent, useEffect, useState } from "react";

import { getConversation, getConversations, sendChatStream, uploadDocument } from "../services/api";
import type { ChatResponse, Citation, ConversationSummary, CurrentDocument, ToolTraceEvent, UploadResponse } from "../types/api";
import { CitationLink } from "./CitationLink";

const initialTutorMessage = "Hỏi mình về lesson, khái niệm, bài giảng, hoặc upload tài liệu riêng để đối chiếu.";

const toolLabels: Record<ToolTraceEvent["tool_name"], string> = {
  request_router: "request_router",
  search_document: "search_document",
  analyse_current_document: "analyse_current_document",
  compare_document_with_course: "compare_document_with_course",
};

function createConversationId(): string {
  return crypto.randomUUID();
}

type TutorChatProps = {
  learnerId: string;
  courseId: string;
  currentLessonId: string | null;
  onOpenCitation: (citation: Citation) => void;
  currentDocument?: CurrentDocument;
  onUploadCompleted: (upload: UploadResponse) => void;
};

type ChatTurn = {
  id: string;
  role: "assistant" | "user";
  content: string;
  response?: ChatResponse;
  toolTrace?: ToolTraceEvent[];
  isPending?: boolean;
  question?: string;
  failed?: boolean;
};

export function TutorChat({ learnerId, courseId, currentLessonId, onOpenCitation, currentDocument, onUploadCompleted }: TutorChatProps) {
  const [message, setMessage] = useState("");
  const [chatTurns, setChatTurns] = useState<ChatTurn[]>([
    {
      id: "welcome",
      role: "assistant",
      content: initialTutorMessage,
    },
  ]);
  const [isSending, setIsSending] = useState(false);
  const [uploads, setUploads] = useState<UploadResponse[]>([]);
  const [conversationId, setConversationId] = useState<string>(createConversationId);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [expandedTraceIds, setExpandedTraceIds] = useState<Set<string>>(new Set());
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
    setConversationId(createConversationId());
    setUploads([]);
    setChatTurns([{ id: "welcome", role: "assistant", content: initialTutorMessage }]);
    setExpandedTraceIds(new Set());
    setIsHistoryOpen(false);
  }

  async function openConversation(id: string) {
    try {
      const conversation = await getConversation(id, learnerId, courseId);
      setConversationId(conversation.conversation_id);
      setUploads([]);
      setChatTurns(conversation.messages.map((item, index) => ({
        id: `history-${index}`,
        role: item.role,
        content: item.content,
        toolTrace: item.tool_trace,
        response: item.role === "assistant"
          ? { conversation_id: conversation.conversation_id, answer: item.content, citations: item.citations, tool_trace: item.tool_trace, confidence: "medium", needs_clarification: false, suggested_next_action: null }
          : undefined,
      })));
      setExpandedTraceIds(new Set());
      setIsHistoryOpen(false);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Không mở được lịch sử chat");
    }
  }

  async function askTutor(nextMessage: string, attachedUploads = uploads) {
    const attachedDocumentIds = attachedUploads.map((upload) => upload.document_id);
    const uploadedDocument = attachedUploads[attachedUploads.length - 1];
    const pendingTurnId = crypto.randomUUID();
    setChatTurns((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", content: nextMessage },
      { id: pendingTurnId, role: "assistant", content: "Đang tìm nguồn và tạo câu trả lời…", toolTrace: [], isPending: true, question: nextMessage },
    ]);
    setMessage("");
    setUploads([]);
    setIsSending(true);
    setError(null);

    try {
      const response = await sendChatStream({
        learner_id: learnerId,
        course_id: courseId,
        message: nextMessage,
        current_lesson_id: currentLessonId ?? undefined,
        current_document: uploadedDocument
          ? {
              source_type: "user_upload",
              source_id: uploadedDocument.source_id,
              title: uploadedDocument.file_name,
              lesson_id: "user-upload",
            }
          : currentDocument,
        uploaded_document_ids: attachedDocumentIds,
        conversation_id: conversationId,
      }, (traceEvent) => {
        setChatTurns((current) => current.map((turn) => (
          turn.id === pendingTurnId
            ? { ...turn, toolTrace: [...(turn.toolTrace ?? []), traceEvent] }
            : turn
        )));
      });
      setConversationId(response.conversation_id);
      setChatTurns((current) => current.map((turn) => (
        turn.id === pendingTurnId
          ? { ...turn, content: response.answer, response, toolTrace: response.tool_trace, isPending: false }
          : turn
      )));
      void refreshHistory();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Không gửi được câu hỏi");
      setChatTurns((current) => current.map((turn) => (
        turn.id === pendingTurnId
          ? { ...turn, content: "Mình chưa thể tạo câu trả lời. Bạn hãy thử lại.", isPending: false, failed: true }
          : turn
      )));
    } finally {
      setIsSending(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextMessage = message.trim();
    if (!nextMessage || isSending) return;
    await askTutor(nextMessage);
  }

  function handleMessageKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey || event.nativeEvent.isComposing) return;
    event.preventDefault();
    if (!isSending && message.trim()) {
      event.currentTarget.form?.requestSubmit();
    }
  }

  async function retryTurn(turn: ChatTurn) {
    if (!turn.question || isSending) return;
    setChatTurns((current) => {
      const assistantIndex = current.findIndex((item) => item.id === turn.id);
      return assistantIndex > 0 ? current.filter((_, index) => index !== assistantIndex && index !== assistantIndex - 1) : current;
    });
    await askTutor(turn.question, []);
  }

  function useSuggestedAction(action: string) {
    setMessage(action);
    requestAnimationFrame(() => document.querySelector<HTMLTextAreaElement>(".chat-composer textarea")?.focus());
  }

  async function copyAnswer(answer: string) {
    try {
      await navigator.clipboard.writeText(answer);
    } catch {
      setError("Không thể sao chép câu trả lời trên trình duyệt này");
    }
  }

  async function handleUpload(file: File | null) {
    if (!file) return;
    setError(null);
    try {
      const response = await uploadDocument(learnerId, conversationId, file);
      setUploads((current) => [...current, response]);
      onUploadCompleted(response);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Không upload được file");
    }
  }

  function toggleTrace(turnId: string) {
    setExpandedTraceIds((current) => {
      const next = new Set(current);
      if (next.has(turnId)) next.delete(turnId);
      else next.add(turnId);
      return next;
    });
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
        {chatTurns.map((turn) => {
          // The trace tab is deliberately limited to calls that reached a document tool.
          // Routing and skipped states are implementation details, not tool executions.
          const trace = (turn.response?.tool_trace ?? turn.toolTrace ?? []).filter(
            (event) => event.tool_name !== "request_router" && event.status !== "skipped",
          );
          const isTraceExpanded = expandedTraceIds.has(turn.id);
          return (
          <article key={turn.id} className={`message-card ${turn.role} ${turn.isPending ? "is-pending" : ""} ${turn.failed ? "is-failed" : ""}`}>
            <div className="message-card-header">
              <strong>{turn.role === "assistant" ? "Tutor" : "Bạn"}</strong>
              {turn.role === "assistant" && turn.response ? <span className={`confidence-badge confidence-${turn.response.confidence}`}>{turn.response.confidence === "high" ? "Tin cậy cao" : turn.response.confidence === "medium" ? "Tin cậy vừa" : "Cần kiểm tra"}</span> : null}
            </div>
            <pre>{turn.content}</pre>
            {turn.role === "assistant" && trace.length > 0 ? (
              <section className="tool-trace">
                <button
                  className="tool-trace-toggle"
                  type="button"
                  aria-expanded={isTraceExpanded}
                  onClick={() => toggleTrace(turn.id)}
                >
                  <span>Suy luận</span>
                  <span aria-hidden="true">{isTraceExpanded ? "⌃" : "⌄"}</span>
                </button>
                {isTraceExpanded ? (
                  <ol className="tool-trace-list">
                    {trace.length ? trace.map((event, traceIndex) => (
                      <li key={`${event.tool_name}-${event.status}-${traceIndex}`} className={`tool-trace-item is-${event.status}`}>
                        <div className="tool-trace-heading">
                          <span className="tool-trace-phase">{event.status === "started" ? "Action" : "Observation"}</span>
                          <code>{toolLabels[event.tool_name]}</code>
                        </div>
                        <span>{event.summary}</span>
                      </li>
                    )) : <li className="tool-trace-empty">Agent đang chuẩn bị xử lý yêu cầu…</li>}
                  </ol>
                ) : null}
              </section>
            ) : null}
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
            {turn.role === "assistant" && turn.response?.suggested_next_action ? (
              <button className="suggested-action" type="button" onClick={() => useSuggestedAction(turn.response?.suggested_next_action ?? "")}>
                <span aria-hidden="true">→</span> {turn.response.suggested_next_action}
              </button>
            ) : null}
            {turn.role === "assistant" && !turn.isPending ? (
              <div className="answer-actions">
                <button type="button" onClick={() => void copyAnswer(turn.content)}>Sao chép</button>
                {turn.failed ? <button type="button" onClick={() => void retryTurn(turn)}>Thử lại</button> : null}
              </div>
            ) : null}
          </article>
          );
        })}
      </section>

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

          <div className="composer-main">
            {uploads.length ? <div className="attachment-chip-list">{uploads.map((upload) => <span key={upload.document_id} className="attachment-chip"><span aria-hidden="true">📎</span><span className="attachment-name">{upload.file_name}</span><small>Đã sẵn sàng để hỏi</small><button type="button" aria-label={`Gỡ ${upload.file_name}`} onClick={() => setUploads((current) => current.filter((item) => item.document_id !== upload.document_id))}>×</button></span>)}</div> : null}
            <textarea
              aria-label="Câu hỏi"
              placeholder="Hỏi về lesson, slide, transcript..."
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={handleMessageKeyDown}
            />
          </div>

          <button className="send-icon-button" type="submit" disabled={isSending} title="Gửi câu hỏi">
            <span aria-hidden="true">{isSending ? "..." : "↑"}</span>
          </button>
        </div>
      </form>

      {error ? <p className="error-text">{error}</p> : null}
    </>
  );
}
