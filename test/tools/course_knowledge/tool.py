from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.tool_registry import Tool


class CourseKnowledgeTool(Tool):
    """
    Tool for searching and retrieving information from course materials.
    Searches through slides, transcripts, and chat history with configurable priority.
    """

    name: str = "course_knowledge"
    description: str = "Search and retrieve information from course materials including slides, transcripts, and chat history"

    def __init__(self, data_root: str = "/d/vinAI/lab05-06/DAY05-2A202601126-BuiThaiSon/data/vlearn-pack") -> None:
        super().__init__()
        self.data_root = Path(data_root)
        self.chatlog_path = self.data_root / "chatlog" / "chat_history_anonymized_for_hackathon.csv"
        self.transcript_dir = self.data_root / "transcript"
        self.slides_dir = self.data_root / "slides"

        # Cache for chat data to avoid reloading
        self._chat_data: Optional[List[Dict[str, Any]]] = None
        self._transcript_cache: Dict[str, str] = {}
        self._slides_cache: Dict[str, str] = {}

    def execute(
        self,
        query: str,
        source_priority: str = "current_lesson",
        max_results: int = 5,
        current_lesson: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Search course materials for information related to the query.

        Args:
            query: Search query
            source_priority: Priority order for searching knowledge sources
            max_results: Maximum number of results to return
            current_lesson: Current lesson being studied (for priority-based search)
            **kwargs: Additional arguments

        Returns:
            Dict containing search results and metadata
        """
        try:
            results = []

            # Determine search order based on priority
            search_order = self._get_search_order(source_priority, current_lesson)

            # Search each source type in order
            for source_type in search_order:
                source_results = self._search_source(source_type, query, max_results - len(results))
                results.extend(source_results)

                # Stop if we have enough results
                if len(results) >= max_results:
                    break

            # Limit results to max_results
            results = results[:max_results]

            return {
                "query": query,
                "results": results,
                "total_found": len(results),
                "sources_searched": search_order,
                "message": f"Found {len(results)} results for query: '{query}'"
            }

        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error searching course knowledge: {str(e)}",
                "query": query
            }

    def _get_search_order(self, source_priority: str, current_lesson: Optional[str]) -> List[str]:
        """Get the search order based on priority setting."""
        # Base priority order
        priority_map = {
            "current_lesson": ["current_lesson", "current_transcript", "other_lessons", "other_transcripts", "chat_history", "conversation_memory", "uploaded_docs"],
            "current_transcript": ["current_transcript", "current_lesson", "other_lessons", "other_transcripts", "chat_history", "conversation_memory", "uploaded_docs"],
            "other_lessons": ["other_lessons", "current_lesson", "current_transcript", "other_transcripts", "chat_history", "conversation_memory", "uploaded_docs"],
            "other_transcripts": ["other_transcripts", "current_transcript", "current_lesson", "other_lessons", "chat_history", "conversation_memory", "uploaded_docs"],
            "chat_history": ["chat_history", "current_lesson", "current_transcript", "other_lessons", "other_transcripts", "conversation_memory", "uploaded_docs"],
            "conversation_memory": ["conversation_memory", "chat_history", "current_lesson", "current_transcript", "other_lessons", "other_transcripts", "uploaded_docs"],
            "uploaded_docs": ["uploaded_docs", "chat_history", "conversation_memory", "current_lesson", "current_transcript", "other_lessons", "other_transcripts"]
        }

        return priority_map.get(source_priority, priority_map["current_lesson"])

    def _search_source(self, source_type: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search a specific source type for the query."""
        if source_type == "current_lesson":
            return self._search_current_lesson(query, max_results)
        elif source_type == "current_transcript":
            return self._search_current_transcript(query, max_results)
        elif source_type == "other_lessons":
            return self._search_other_lessons(query, max_results)
        elif source_type == "other_transcripts":
            return self._search_other_transcripts(query, max_results)
        elif source_type == "chat_history":
            return self._search_chat_history(query, max_results)
        elif source_type == "conversation_memory":
            # This would integrate with conversation memory tool - for now return empty
            return []
        elif source_type == "uploaded_docs":
            # This would integrate with external learning tool - for now return empty
            return []
        else:
            return []

    def _search_current_lesson(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search materials related to the current lesson."""
        # In a full implementation, this would determine the current lesson from context
        # For now, we'll search all materials but label them appropriately
        results = []

        # Search transcripts
        transcript_results = self._search_transcripts(query, max_results // 2)
        for result in transcript_results:
            result["source_type"] = "transcript"
            result["priority"] = "current_lesson"
            results.append(result)

        # Search slides
        slides_results = self._search_slides(query, max_results - len(results))
        for result in slides_results:
            result["source_type"] = "slide"
            result["priority"] = "current_lesson"
            results.append(result)

        return results[:max_results]

    def _search_current_transcript(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search current transcript (simplified - searches all transcripts)."""
        return self._search_transcripts(query, max_results)

    def _search_other_lessons(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search other lessons (simplified - same as other transcripts for now)."""
        return self._search_other_transcripts(query, max_results)

    def _search_other_transcripts(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search transcripts (all transcripts treated as 'other' for simplicity)."""
        return self._search_transcripts(query, max_results)

    def _search_chat_history(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search chat history for tutor-student interactions."""
        try:
            chat_data = self._load_chat_data()
            results = []

            query_lower = query.lower()
            query_terms = set(re.findall(r'\b\w+\b', query_lower))

            for entry in chat_data:
                # Search in both student and tutor messages
                content = entry.get("content", "").lower()
                if any(term in content for term in query_terms):
                    # Calculate simple relevance score
                    score = sum(1 for term in query_terms if term in content)

                    results.append({
                        "content": entry.get("content", ""),
                        "role": entry.get("role", ""),
                        "turn_id": entry.get("turn_id", ""),
                        "conversation_id": entry.get("conversation_id", ""),
                        "day_code": entry.get("day_code", ""),
                        "move_used": entry.get("move_used", ""),  # Tutor strategy used
                        "citations": entry.get("citations", []),
                        "relevance_score": score,
                        "source": "chat_history",
                        "source_type": "chat_history",
                        "priority": "chat_history"
                    })

            # Sort by relevance score (descending) and limit results
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results[:max_results]

        except Exception as e:
            return [{
                "error": type(e).__name__,
                "message": f"Error searching chat history: {str(e)}",
                "source": "chat_history"
            }]

    def _search_transcripts(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search transcript files."""
        results = []
        query_lower = query.lower()
        query_terms = set(re.findall(r'\b\w+\b', query_lower))

        try:
            for transcript_file in self.transcript_dir.glob("*.md"):
                if transcript_file.name in self._transcript_cache:
                    content = self._transcript_cache[transcript_file.name]
                else:
                    content = transcript_file.read_text(encoding="utf-8")
                    self._transcript_cache[transcript_file.name] = content

                # Look for citation markers and content
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    if any(term in line_lower for term in query_terms):
                        # Extract surrounding context
                        start_idx = max(0, i - 2)
                        end_idx = min(len(lines), i + 3)
                        context_lines = lines[start_idx:end_idx]
                        context = '\n'.join(context_lines)

                        # Extract citation marker if present
                        citation_match = re.search(r'\[T\d{2}-\d{3}\]', line)
                        citation = citation_match.group(0) if citation_match else None

                        results.append({
                            "content": context.strip(),
                            "line_number": i + 1,
                            "citation": citation,
                            "transcript_file": transcript_file.name,
                            "source": "transcript",
                            "source_type": "transcript",
                            "priority": "transcript"
                        })

                        if len(results) >= max_results:
                            break

                if len(results) >= max_results:
                    break

        except Exception as e:
            return [{
                "error": type(e).__name__,
                "message": f"Error searching transcripts: {str(e)}",
                "source": "transcript"
            }]

        return results[:max_results]

    def _search_slides(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search slide files (PDF files - simplified text search)."""
        results = []
        query_lower = query.lower()
        query_terms = set(re.findall(r'\b\w+\b', query_lower))

        try:
            # For PDF files, we'd need a PDF library - for now, we'll note that slides exist
            # In a full implementation, we would use PyPDF2 or similar to extract text
            for slide_file in self.slides_dir.glob("*.pdf"):
                # Placeholder result indicating slide contains relevant information
                # In reality, we'd extract text from PDF and search it
                results.append({
                    "content": f"[Slide content from {slide_file.name} would be searched - PDF text extraction needed]",
                    "slide_file": slide_file.name,
                    "source": "slides",
                    "source_type": "slide",
                    "priority": "slides",
                    "note": "PDF text extraction not implemented in this version"
                })

                if len(results) >= max_results:
                    break

        except Exception as e:
            return [{
                "error": type(e).__name__,
                "message": f"Error searching slides: {str(e)}",
                "source": "slides"
            }]

        return results[:max_results]

    def _load_chat_data(self) -> List[Dict[str, Any]]:
        """Load and cache chat history data."""
        if self._chat_data is not None:
            return self._chat_data

        try:
            chat_data = []
            with open(self.chatlog_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    chat_data.append(row)
            self._chat_data = chat_data
            return chat_data
        except Exception as e:
            # Return empty list if file can't be read
            return []