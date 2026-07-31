import { useState } from 'react';
import type { FC } from 'react';
import type { Lesson } from '../types/agent';
import { BookOpen, FileText, Search, GraduationCap, CheckCircle2, ChevronRight, Layers } from 'lucide-react';

interface LessonPanelProps {
  lessons: Lesson[];
  selectedLessonId: string | null;
  onLessonSelect: (lesson: Lesson) => void;
  currentPage: number;
  totalPages: number;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const LessonPanel: FC<LessonPanelProps> = ({
  lessons,
  selectedLessonId,
  onLessonSelect,
  currentPage,
  totalPages,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredLessons = lessons.filter(
    (lesson) =>
      lesson.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (lesson.description && lesson.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <aside className="w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full shadow-sm transition-all duration-300">
      {/* Panel Header */}
      <div className="p-4 border-b border-slate-100 dark:border-slate-800/80">
        <div className="flex items-center space-x-2 mb-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-500/20">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800 dark:text-slate-100 tracking-tight">
              Course Modules
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Deep Learning Curriculum
            </p>
          </div>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search modules..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-lg border border-transparent focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 focus:outline-none transition-all"
          />
        </div>
      </div>

      {/* Lesson List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        <div className="px-2 pb-1 text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider flex items-center justify-between">
          <span>Available Lessons ({filteredLessons.length})</span>
          <Layers className="w-3 h-3" />
        </div>

        {filteredLessons.map((lesson, idx) => {
          const isSelected = selectedLessonId === lesson.id;
          return (
            <button
              key={lesson.id}
              onClick={() => onLessonSelect(lesson)}
              className={`w-full text-left p-3 rounded-xl transition-all duration-200 group relative border ${
                isSelected
                  ? 'bg-indigo-50/80 dark:bg-indigo-950/40 border-indigo-200 dark:border-indigo-800/60 text-indigo-900 dark:text-indigo-200 shadow-sm'
                  : 'bg-white dark:bg-slate-900/50 border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:border-slate-200 dark:hover:border-slate-700 text-slate-700 dark:text-slate-300'
              }`}
            >
              {isSelected && (
                <div className="absolute left-0 top-3 bottom-3 w-1 bg-indigo-600 rounded-r-full" />
              )}
              
              <div className="flex items-start space-x-3">
                <div
                  className={`mt-0.5 p-2 rounded-lg transition-colors ${
                    isSelected
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400'
                  }`}
                >
                  <BookOpen className="w-4 h-4" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Module 0{idx + 1}
                    </span>
                    {isSelected && (
                      <span className="inline-flex items-center text-[10px] font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-100/80 dark:bg-indigo-900/50 px-1.5 py-0.5 rounded-full">
                        Active
                      </span>
                    )}
                  </div>
                  
                  <h3
                    className={`text-xs font-bold leading-tight mt-0.5 line-clamp-2 ${
                      isSelected
                        ? 'text-indigo-950 dark:text-indigo-100'
                        : 'text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400'
                    }`}
                  >
                    {lesson.name}
                  </h3>

                  {lesson.description && (
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                      {lesson.description}
                    </p>
                  )}

                  <div className="flex items-center space-x-2 mt-2 pt-2 border-t border-slate-100 dark:border-slate-800/60 text-[10px] text-slate-400 dark:text-slate-500">
                    <span className="inline-flex items-center space-x-1">
                      <FileText className="w-3 h-3 text-slate-400" />
                      <span className="truncate max-w-[120px]">{lesson.file}</span>
                    </span>
                    <ChevronRight className="w-3 h-3 ml-auto opacity-0 group-hover:opacity-100 transition-opacity text-indigo-500" />
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Progress Footer */}
      <div className="p-4 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/40">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-medium text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
            Current Reading
          </span>
          <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
            Page {currentPage} {totalPages > 0 ? `/ ${totalPages}` : ''}
          </span>
        </div>
        
        <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div
            className="bg-gradient-to-r from-indigo-500 to-purple-600 h-full rounded-full transition-all duration-300"
            style={{
              width: totalPages > 0 ? `${Math.min(100, (currentPage / totalPages) * 100)}%` : '0%',
            }}
          />
        </div>
      </div>
    </aside>
  );
};