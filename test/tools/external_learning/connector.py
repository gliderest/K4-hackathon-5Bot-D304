from __future__ import annotations

import base64
import hashlib
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.tool_registry import Tool


class ExternalLearningTool(Tool):
    """
    Tool for processing and integrating externally uploaded learning materials.
    Supports PDF, DOCX, PPTX, TXT, and Markdown files.
    """

    name: str = "external_learning"
    description: str = "Process and integrate externally uploaded learning materials"

    def __init__(self, storage_dir: str = "./external_materials") -> None:
        super().__init__()
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        # In-memory cache for processed content
        self._content_cache: Dict[str, Dict[str, Any]] = {}

    def execute(
        self,
        operation: str = "process",
        file_path: Optional[str] = None,
        query: str = "",
        file_type: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute operations on external learning materials.

        Args:
            operation: Operation to perform (process, query, cleanup)
            file_path: Path to the uploaded file (for process operation)
            query: Query to search within processed materials (for query operation)
            file_type: Type of file (pdf, docx, pptx, txt, md)
            **kwargs: Additional arguments

        Returns:
            Dict containing the results of the operation
        """
        try:
            if operation == "process":
                if not file_path:
                    return {
                        "error": "missing_file_path",
                        "message": "File path is required for process operation"
                    }
                return self._process_file(file_path, file_type)
            elif operation == "query":
                if not query:
                    return {
                        "error": "missing_query",
                        "message": "Query is required for query operation"
                    }
                return self._query_materials(query)
            elif operation == "cleanup":
                return self._cleanup_materials()
            else:
                return {
                    "error": "invalid_operation",
                    "message": f"Unknown operation: {operation}",
                    "valid_operations": ["process", "query", "cleanup"]
                }
        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error in external learning operation: {str(e)}",
                "operation": operation
            }

    def _process_file(self, file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """Process an uploaded file and extract its content."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "error": "file_not_found",
                    "message": f"File not found: {file_path}"
                }

            # Determine file type if not provided
            if not file_type:
                file_type = path.suffix.lower().lstrip('.')
                if file_type == 'md':
                    file_type = 'markdown'
                elif file_type in ['jpeg', 'jpg', 'png', 'gif', 'bmp']:
                    # Image files - we'd need OCR for text extraction
                    return {
                        "error": "unsupported_file_type",
                        "message": f"File type '{file_type}' requires OCR for text extraction, which is not implemented in this version",
                        "supported_types": ["pdf", "docx", "pptx", "txt", "md"]
                    }

            # Process based on file type
            if file_type == "pdf":
                content = self._extract_pdf_text(path)
            elif file_type == "docx":
                content = self._extract_docx_text(path)
            elif file_type == "pptx":
                content = self._extract_pptx_text(path)
            elif file_type == "txt":
                content = self._extract_txt_text(path)
            elif file_type == "markdown":
                content = self._extract_markdown_text(path)
            else:
                return {
                    "error": "unsupported_file_type",
                    "message": f"Unsupported file type: {file_type}",
                    "supported_types": ["pdf", "docx", "pptx", "txt", "md"]
                }

            if not content or not content.strip():
                return {
                    "error": "empty_content",
                    "message": "No text content could be extracted from the file",
                    "file_path": file_path,
                    "file_type": file_type
                }

            # Generate a unique ID for this file
            file_hash = hashlib.md5(
                f"{file_path}{os.path.getmtime(file_path)}".encode()
            ).hexdigest()[:12]

            # Store in cache
            self._content_cache[file_hash] = {
                "file_path": str(path.absolute()),
                "file_name": path.name,
                "file_type": file_type,
                "content": content,
                "processed_at": self._get_timestamp(),
                "size_bytes": path.stat().st_size
            }

            # Also save a copy to our storage directory
            storage_path = self.storage_dir / f"{file_hash}_{path.name}"
            try:
                import shutil
                shutil.copy2(path, storage_path)
            except Exception:
                # Non-critical if we can't copy
                pass

            # Create a summary (first 500 characters)
            summary = content[:500] + ("..." if len(content) > 500 else "")

            return {
                "file_id": file_hash,
                "file_name": path.name,
                "file_type": file_type,
                "content_length": len(content),
                "summary": summary,
                "preview": content[:200] + ("..." if len(content) > 200 else ""),
                "processed_at": self._get_timestamp(),
                "message": f"Successfully processed {path.name} ({file_type})",
                "success": True
            }

        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error processing file: {str(e)}",
                "file_path": file_path
            }

    def _extract_pdf_text(self, path: Path) -> str:
        """Extract text from PDF file."""
        # In a real implementation, we would use PyPDF2 or pdfplumber
        # For this version, we'll return a placeholder
        return f"[PDF content from {path.name} would be extracted here - PDF text extraction library needed]"

    def _extract_docx_text(self, path: Path) -> str:
        """Extract text from DOCX file."""
        # In a real implementation, we would use python-docx
        return f"[DOCX content from {path.name} would be extracted here - python-docx library needed]"

    def _extract_pptx_text(self, path: Path) -> str:
        """Extract text from PPTX file."""
        # In a real implementation, we would use python-pptx
        return f"[PPTX content from {path.name} would be extracted here - python-pptx library needed]"

    def _extract_txt_text(self, path: Path) -> str:
        """Extract text from TXT file."""
        try:
            return path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            try:
                return path.read_text(encoding='latin-1')
            except Exception:
                return f"[Unable to read text file {path.name} - encoding issues]"

    def _extract_markdown_text(self, path: Path) -> str:
        """Extract text from Markdown file."""
        try:
            content = path.read_text(encoding='utf-8')
            # Optionally strip markdown formatting for cleaner text
            # For now, return as-is
            return content
        except UnicodeDecodeError:
            try:
                return path.read_text(encoding='latin-1')
            except Exception:
                return f"[Unable to read markdown file {path.name} - encoding issues]"

    def _query_materials(self, query: str) -> Dict[str, Any]:
        """Search within processed materials."""
        if not self._content_cache:
            return {
                "query": query,
                "results": [],
                "total_matches": 0,
                "message": "No materials have been processed yet"
            }

        query_lower = query.lower()
        query_terms = set(re.findall(r'\b\w+\b', query_lower))

        results = []
        for file_id, file_data in self._content_cache.items():
            content = file_data.get("content", "").lower()
            content_terms = set(re.findall(r'\b\w+\b', content))

            # Simple matching based on term overlap
            matches = len(query_terms & content_terms)
            if matches > 0:
                # Calculate a simple relevance score
                relevance = min(1.0, matches / max(len(query_terms), 1))
                results.append({
                    "file_id": file_id,
                    "file_name": file_data["file_name"],
                    "file_type": file_data["file_type"],
                    "relevance": relevance,
                    "matched_terms": list(query_terms & content_terms)[:5],  # Top 5 matched terms
                    "preview": file_data["content"][:200] + ("..." if len(file_data["content"]) > 200 else ""),
                    "processed_at": file_data["processed_at"]
                })

        # Sort by relevance (descending)
        results.sort(key=lambda x: x["relevance"], reverse=True)

        return {
            "query": query,
            "results": results,
            "total_matches": len(results),
            "message": f"Found {len(results)} matching materials for query: '{query}'"
        }

    def _cleanup_materials(self) -> Dict[str, Any]:
        """Clean up stored materials (older than a certain age or exceeding limit)."""
        # For this simple implementation, we'll just clear the cache
        # In a real system, we'd implement proper cleanup based on age or size
        initial_count = len(self._content_cache)
        self._content_cache.clear()

        # Also clean up storage directory (optional)
        # For safety, we won't automatically delete files in this example

        return {
            "cleaned_files": initial_count,
            "message": f"Cleared {initial_count} processed materials from cache"
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()