import type { FC } from 'react';
import { Sun, Moon, Cpu, PanelLeftClose, PanelLeftOpen, CircleCheck, AlertTriangle } from 'lucide-react';

interface HeaderProps {
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
  isBackendConnected: boolean;
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export const Header: FC<HeaderProps> = ({
  isDarkMode,
  onToggleDarkMode,
  isBackendConnected,
  isSidebarOpen,
  onToggleSidebar,
}) => {
  return (
    <header className="h-14 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 flex items-center justify-between z-20 shadow-xs">
      <div className="flex items-center space-x-3">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title={isSidebarOpen ? 'Ẩn thanh bên' : 'Hiện thanh bên'}
        >
          {isSidebarOpen ? <PanelLeftClose className="w-5 h-5" /> : <PanelLeftOpen className="w-5 h-5" />}
        </button>

        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-lg bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-sm">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI Tutor Lab
            </h1>
            <p className="text-[10px] text-slate-400 dark:text-slate-500 -mt-0.5">
              Trợ lý Học tập Thông minh
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Backend Status Badge */}
        <div
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
            isBackendConnected
              ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60'
              : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800/60'
          }`}
        >
          {isBackendConnected ? (
            <>
              <CircleCheck className="w-3.5 h-3.5 text-emerald-500" />
              <span>Đã kết nối Backend</span>
            </>
          ) : (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
              <span>Chế độ Ngoại tuyến</span>
            </>
          )}
        </div>

        {/* Dark Mode Toggle */}
        <button
          onClick={onToggleDarkMode}
          className="p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
          title={isDarkMode ? 'Chuyển sang Chế độ Sáng' : 'Chuyển sang Chế độ Tối'}
        >
          {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>
      </div>
    </header>
  );
};
