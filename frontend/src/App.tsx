import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { LessonPanel } from './components/LessonPanel';
import { PdfViewerPanel } from './components/PdfViewerPanel';
import { ChatPanel } from './components/ChatPanel';
import { apiService } from './services/api';
import type { Lesson, ChatMessage } from './types/agent';

const DEFAULT_LESSONS: Lesson[] = [
  {
    id: 'd1-slide-hackathon',
    name: 'Day 1: Introduction to Deep Learning',
    description: 'Fundamentals of Neural Networks, Architectures & Activation Functions',
    file: 'd1-slide-hackathon.pdf',
  },
  {
    id: 'd2-slide-hackathon',
    name: 'Day 2: Advanced Neural Networks',
    description: 'Deep Learning Optimization, Loss Functions & Modern Architectures',
    file: 'd2-slide-hackathon.pdf',
  },
];

export function App() {
  const [lessons, setLessons] = useState<Lesson[]>(DEFAULT_LESSONS);
  const [selectedLesson, setSelectedLesson] = useState<Lesson>(DEFAULT_LESSONS[0]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-msg',
      role: 'assistant',
      content: `Hello! 👋 I'm your AI Learning Assistant. I can help answer questions, summarize slides, or explain concepts from **${selectedLesson.name}**. Feel free to ask anything!`,
      timestamp: new Date(),
    },
  ]);

  const [isThinking, setIsThinking] = useState<boolean>(false);
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);

  // Check backend health periodically
  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await apiService.checkHealth();
      setIsBackendConnected(healthy);
    };

    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch lessons if available
  useEffect(() => {
    apiService.getLessons().then((fetchedLessons) => {
      if (fetchedLessons && fetchedLessons.length > 0) {
        setLessons(fetchedLessons);
      }
    });
  }, []);

  // Dark mode handler
  const handleToggleDarkMode = () => {
    setIsDarkMode((prev) => {
      const next = !prev;
      if (next) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return next;
    });
  };

  const handleLessonSelect = (lesson: Lesson) => {
    setSelectedLesson(lesson);
    setCurrentPage(1);
  };

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsThinking(true);

    const context = {
      current_lesson: selectedLesson.name,
      current_page: currentPage,
      file: selectedLesson.file,
    };

    try {
      const responseData = await apiService.chat(text, context);
      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseData.response || "I didn't receive a response text.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error: any) {
      console.error('Chat error:', error);
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `⚠️ **Unable to connect to AI server at http://localhost:8000**\n\n*Error details:* ${
          error.message || 'Server unavailable'
        }\n\n*To start the backend server:* Run \`python server.py\` in the \`test/\` folder.`,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Chat history cleared. How can I help you study **${selectedLesson.name}**?`,
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* Top Navigation Header */}
      <Header
        isDarkMode={isDarkMode}
        onToggleDarkMode={handleToggleDarkMode}
        isBackendConnected={isBackendConnected}
        isSidebarOpen={isSidebarOpen}
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
      />

      {/* Main Content 3-Panel Split View */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Panel: Course Modules */}
        {isSidebarOpen && (
          <LessonPanel
            lessons={lessons}
            selectedLessonId={selectedLesson.id}
            onLessonSelect={handleLessonSelect}
            currentPage={currentPage}
            totalPages={totalPages}
          />
        )}

        {/* Center Panel: PDF Viewer */}
        <PdfViewerPanel
          fileUrl={`/${selectedLesson.file}`}
          lessonName={selectedLesson.name}
          currentPage={currentPage}
          onPageChange={(page) => setCurrentPage(page)}
          onDocumentLoad={(pages) => setTotalPages(pages)}
        />

        {/* Right Panel: AI Tutor Chat */}
        <ChatPanel
          messages={messages}
          onSendMessage={handleSendMessage}
          isThinking={isThinking}
          isBackendConnected={isBackendConnected}
          selectedLesson={selectedLesson}
          currentPage={currentPage}
          onClearChat={handleClearChat}
        />
      </div>
    </div>
  );
}

export default App;