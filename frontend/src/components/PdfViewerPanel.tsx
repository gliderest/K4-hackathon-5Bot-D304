import { useState, useEffect, useRef } from 'react';
import type { FC, ChangeEvent } from 'react';
import { Viewer, Worker } from '@react-pdf-viewer/core';
import type { PageChangeEvent, DocumentLoadEvent } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import { pageNavigationPlugin } from '@react-pdf-viewer/page-navigation';
import '@react-pdf-viewer/page-navigation/lib/styles/index.css';

import {
  ChevronLeft,
  ChevronRight,
  FileText,
  Loader2,
  ZoomIn,
  ZoomOut,
  Maximize2
} from 'lucide-react';

interface PdfViewerPanelProps {
  fileUrl: string;
  lessonName: string;
  currentPage: number;
  onPageChange: (page: number) => void;
  onDocumentLoad?: (totalPages: number) => void;
}

export const PdfViewerPanel: FC<PdfViewerPanelProps> = ({
  fileUrl,
  lessonName,
  currentPage,
  onPageChange,
  onDocumentLoad,
}) => {
  const [totalPages, setTotalPages] = useState<number>(0);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const containerRef = useRef<HTMLDivElement>(null);

  // Plugins
  const pageNavigationPluginInstance = pageNavigationPlugin();
  const { jumpToPage } = pageNavigationPluginInstance;

  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    toolbarPlugin: {
      fullScreenPlugin: {
        onEnterFullScreen: () => {},
        onExitFullScreen: () => {},
      },
    },
  });

  const handleDocumentLoad = (e: DocumentLoadEvent) => {
    setTotalPages(e.doc.numPages);
    setIsLoading(false);
    if (onDocumentLoad) {
      onDocumentLoad(e.doc.numPages);
    }
  };

  const handlePageChange = (e: PageChangeEvent) => {
    const newPage = e.currentPage + 1;
    if (newPage !== currentPage) {
      onPageChange(newPage);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      const target = currentPage - 1;
      jumpToPage(target - 1);
      onPageChange(target);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      const target = currentPage + 1;
      jumpToPage(target - 1);
      onPageChange(target);
    }
  };

  const handlePageInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value, 10);
    if (!isNaN(val) && val >= 1 && val <= totalPages) {
      jumpToPage(val - 1);
      onPageChange(val);
    }
  };

  const toggleFullScreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch((err) => {
        console.error(`Error attempting to enable full-screen mode: ${err.message}`);
      });
    } else {
      document.exitFullscreen();
    }
  };

  // Synchronize jumpToPage if currentPage prop changes externally
  useEffect(() => {
    if (currentPage > 0 && totalPages > 0) {
      jumpToPage(currentPage - 1);
    }
  }, [currentPage, totalPages, jumpToPage]);

  return (
    <div ref={containerRef} className="flex-1 flex flex-col h-full bg-slate-100 dark:bg-slate-950 relative overflow-hidden">
      {/* Top Header Toolbar */}
      <div className="h-12 bg-white/90 dark:bg-slate-900/90 backdrop-blur border-b border-slate-200 dark:border-slate-800 px-4 flex items-center justify-between z-10">
        <div className="flex items-center space-x-2 min-w-0">
          <FileText className="w-4 h-4 text-indigo-600 dark:text-indigo-400 flex-shrink-0" />
          <h1 className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
            {lessonName}
          </h1>
        </div>

        {/* Custom PDF Navigation Controls */}
        <div className="flex items-center space-x-3">
          {/* Zoom controls */}
          <div className="hidden sm:flex items-center space-x-1 bg-slate-100 dark:bg-slate-800/80 rounded-lg p-1 border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.2))}
              title="Zoom Out"
              className="p-1 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 rounded transition-colors"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[11px] font-mono text-slate-600 dark:text-slate-400 px-1">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.2))}
              title="Zoom In"
              className="p-1 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 rounded transition-colors"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Fullscreen Button */}
          <button
            onClick={toggleFullScreen}
            title="Toggle Fullscreen"
            className="p-1.5 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 transition-colors"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Viewer Area */}
      <div className="flex-1 relative overflow-auto bg-slate-100 dark:bg-slate-950 flex justify-center items-center">
        {isLoading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm z-20">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mb-2" />
            <p className="text-xs font-medium text-slate-600 dark:text-slate-400">Loading document...</p>
          </div>
        )}

        <div className="w-full h-full" style={{ zoom: zoomLevel }}>
          <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js">
            <Viewer
              fileUrl={fileUrl}
              onDocumentLoad={handleDocumentLoad}
              onPageChange={handlePageChange}
              plugins={[pageNavigationPluginInstance, defaultLayoutPluginInstance]}
            />
          </Worker>
        </div>
      </div>

      {/* Floating Bottom Control Bar */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200/80 dark:border-slate-700/80 px-4 py-2 rounded-2xl shadow-xl flex items-center space-x-3 z-30 transition-all">
        <button
          onClick={handlePrevPage}
          disabled={currentPage <= 1}
          className="p-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-indigo-600 hover:text-white disabled:opacity-30 disabled:hover:bg-slate-100 disabled:hover:text-slate-700 transition-all shadow-sm"
          title="Previous Page"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        <div className="flex items-center space-x-1.5 text-xs font-medium text-slate-700 dark:text-slate-300">
          <span>Page</span>
          <input
            type="number"
            min={1}
            max={totalPages || 1}
            value={currentPage}
            onChange={handlePageInputChange}
            className="w-10 text-center py-0.5 font-bold bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900 dark:text-slate-100"
          />
          <span className="text-slate-400 dark:text-slate-500">of {totalPages || 1}</span>
        </div>

        <button
          onClick={handleNextPage}
          disabled={currentPage >= totalPages}
          className="p-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-indigo-600 hover:text-white disabled:opacity-30 disabled:hover:bg-slate-100 disabled:hover:text-slate-700 transition-all shadow-sm"
          title="Next Page"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
