import { useState, useRef, useEffect } from 'react';
import type { FC } from 'react';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage, Lesson } from '../types/agent';
import {
  Bot,
  User,
  Send,
  Sparkles,
  RotateCcw,
  HelpCircle,
  BookOpen,
  Check,
  Copy,
  Lightbulb
} from 'lucide-react';

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  isThinking: boolean;
  isBackendConnected: boolean;
  selectedLesson: Lesson;
  currentPage: number;
  onClearChat: () => void;
}

export const ChatPanel: FC<ChatPanelProps> = ({
  messages,
  onSendMessage,
  isThinking,
  isBackendConnected,
  selectedLesson,
  currentPage,
  onClearChat,
}) => {
  const [input, setInput] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  const handleSend = () => {
    if (!input.trim() || isThinking) return;
    onSendMessage(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const quickPrompts = [
    `Summarize page ${currentPage} of ${selectedLesson.name}`,
    `Explain the key concepts on page ${currentPage}`,
    `Generate a short quiz for this lesson`,
    `What are the main definitions here?`,
  ];

  return (
    <aside className="w-80 lg:w-96 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 flex flex-col h-full shadow-sm">
      {/* Header */}
      <div className="p-4 border-b border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 text-white shadow-md shadow-indigo-500/20">
              <Bot className="w-5 h-5" />
            </div>
            <span
              className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white dark:border-slate-900 ${
                isBackendConnected ? 'bg-emerald-500' : 'bg-amber-500'
              }`}
              title={isBackendConnected ? 'Backend Connected' : 'Offline / Standby'}
            />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-slate-800 dark:text-slate-100">
                AI Learning Companion
              </h2>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-indigo-500 inline" />
              Powered by OpenRouter LLM
            </p>
          </div>
        </div>

        <button
          onClick={onClearChat}
          title="Clear Conversation"
          className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Active Context Banner */}
      <div className="px-4 py-2 bg-indigo-50/70 dark:bg-indigo-950/30 border-b border-indigo-100/50 dark:border-indigo-900/30 flex items-center justify-between text-[11px]">
        <span className="text-indigo-900 dark:text-indigo-300 font-medium truncate flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 flex-shrink-0" />
          <span className="truncate">{selectedLesson.name}</span>
        </span>
        <span className="bg-indigo-200/80 dark:bg-indigo-900/80 text-indigo-800 dark:text-indigo-200 px-2 py-0.5 rounded-full font-bold text-[10px] flex-shrink-0 ml-2">
          Page {currentPage}
        </span>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8 px-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto mb-3">
              <Lightbulb className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              Ask your AI Tutor anything!
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Select a quick prompt below or type your question about page {currentPage}.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex space-x-2.5 ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-0.5">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`group relative max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed transition-all ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-sm rounded-tr-xs'
                  : msg.isError
                  ? 'bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 rounded-tl-xs'
                  : 'bg-slate-100 dark:bg-slate-800/90 text-slate-800 dark:text-slate-100 rounded-tl-xs border border-slate-200/50 dark:border-slate-700/50'
              }`}
            >
              {msg.role === 'assistant' ? (
                <div className="prose prose-xs dark:prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-slate-900 prose-pre:text-slate-100 prose-pre:rounded-lg">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              )}

              {/* Copy action for assistant responses */}
              {msg.role === 'assistant' && (
                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 dark:bg-slate-800/80 backdrop-blur rounded p-1">
                  <button
                    onClick={() => handleCopy(msg.content, msg.id)}
                    className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                    title="Copy message"
                  >
                    {copiedId === msg.id ? (
                      <Check className="w-3 h-3 text-emerald-500" />
                    ) : (
                      <Copy className="w-3 h-3" />
                    )}
                  </button>
                </div>
              )}

              <span
                className={`block text-[9px] mt-1 text-right ${
                  msg.role === 'user'
                    ? 'text-indigo-200'
                    : 'text-slate-400 dark:text-slate-500'
                }`}
              >
                {new Date(msg.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>

            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {/* Thinking Indicator */}
        {isThinking && (
          <div className="flex space-x-2.5 items-center">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-slate-100 dark:bg-slate-800/90 rounded-2xl rounded-tl-xs p-3 border border-slate-200/50 dark:border-slate-700/50 flex items-center space-x-2">
              <span className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium ml-1">
                Thinking...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Chips */}
      <div className="px-3 py-2 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/40">
        <div className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
          <HelpCircle className="w-3 h-3 text-indigo-500" />
          Suggested Questions
        </div>
        <div className="flex flex-wrap gap-1.5">
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onSendMessage(prompt)}
              disabled={isThinking}
              className="text-[11px] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/80 hover:border-indigo-400 dark:hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-300 text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-full transition-all text-left truncate max-w-full disabled:opacity-50"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Box */}
      <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isThinking}
            placeholder={`Ask AI about Page ${currentPage}...`}
            className="w-full pl-3 pr-10 py-2.5 text-xs bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-xl border border-transparent focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 focus:outline-none transition-all placeholder:text-slate-400"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isThinking}
            className="absolute right-1.5 p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-40 disabled:hover:bg-indigo-600 transition-all shadow-sm"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
};
