from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from agents.tool_registry import Tool


class CitationTool(Tool):
    """
    Tool for formatting and managing citations from course materials.
    Handles extraction, formatting, and validation of citations from transcripts, slides, etc.
    """

    name: str = "citation"
    description: str = "Format and manage citations from course materials"

    def __init__(self) -> None:
        super().__init__()

    def execute(
        self,
        action: str = "extract",
        content: str = "",
        citation_format: str = "inline",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute citation operations.

        Args:
            action: Operation to perform (extract, format, validate)
            content: Text content to extract citations from
            citation_format: Format for citations (inline, bibliography, apa, mla)
            **kwargs: Additional arguments

        Returns:
            Dict containing the results of the citation operation
        """
        try:
            if action == "extract":
                return self._extract_citations(content)
            elif action == "format":
                return self._format_citations(content, citation_format)
            elif action == "validate":
                return self._validate_citations(content)
            else:
                return {
                    "error": "invalid_action",
                    "message": f"Unknown action: {action}",
                    "valid_actions": ["extract", "format", "validate"]
                }
        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error processing citations: {str(e)}",
                "action": action
            }

    def _extract_citations(self, content: str) -> Dict[str, Any]:
        """Extract citations from content."""
        if not content:
            return {
                "citations": [],
                "count": 0,
                "message": "No content provided for citation extraction"
            }

        # Pattern for transcript citations: [Txx-NNN] where xx is 01-06 and NNN is 000-999
        transcript_pattern = r'\[T\d{2}-\d{3}\]'

        # Pattern for slide citations: could be slide numbers or page numbers
        slide_patterns = [
            r'\[slide\s+(\d+)\]',  # [slide 5]
            r'\[Slide\s+(\d+)\]',  # [Slide 5]
            r'\[p\.?\s*(\d+)\]',   # [p. 5] or [p5]
            r'\[page\s+(\d+)\]',   # [page 5]
            r'\[Page\s+(\d+)\]',   # [Page 5]
        ]

        # Pattern for lesson references
        lesson_pattern = r'\[(day\d+(?:-[a-zA-Z0-9]+)?)\]'  # [day02-c301]

        citations = []

        # Extract transcript citations
        transcript_matches = re.findall(transcript_pattern, content)
        for match in transcript_matches:
            citations.append({
                "type": "transcript",
                "citation": match,
                "description": "Transcript segment reference",
                "source": "transcript",
                "original_text": match
            })

        # Extract slide citations
        for pattern in slide_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                citations.append({
                    "type": "slide",
                    "citation": match,
                    "description": "Slide reference",
                    "source": "slides",
                    "original_text": f"[{match}]" if match.isdigit() else match
                })

        # Extract lesson references
        lesson_matches = re.findall(lesson_pattern, content)
        for match in lesson_matches:
            citations.append({
                "type": "lesson",
                "citation": match,
                "description": "Lesson reference",
                "source": "course_materials",
                "original_text": f"[{match}]"
            })

        # Remove duplicates while preserving order
        seen = set()
        unique_citations = []
        for cit in citations:
            # Create a key for deduplication
            key = (cit["type"], cit["citation"])
            if key not in seen:
                seen.add(key)
                unique_citations.append(cit)

        return {
            "citations": unique_citations,
            "count": len(unique_citations),
            "message": f"Extracted {len(unique_citations)} citations from content"
        }

    def _format_citations(self, content: str, citation_format: str) -> Dict[str, Any]:
        """Format citations in the specified format."""
        # First extract citations
        extraction_result = self._extract_citations(content)
        citations = extraction_result.get("citations", [])

        if not citations:
            return {
                "formatted_content": content,
                "citations": [],
                "message": "No citations found to format"
            }

        formatted_content = content

        if citation_format == "inline":
            # Keep citations as they are (already inline)
            formatted_content = content
            citation_text = "Citations kept in inline format"

        elif citation_format == "bibliography":
            # Move citations to a bibliography section at the end
            bibliography_entries = []
            for i, cit in enumerate(citations, 1):
                if cit["type"] == "transcript":
                    bibliography_entries.append(f"[{i}] Transcript: {cit['citation']}")
                elif cit["type"] == "slide":
                    bibliography_entries.append(f"[{i}] Slide: {cit['citation']}")
                elif cit["type"] == "lesson":
                    bibliography_entries.append(f"[{i}] Lesson: {cit['citation']}")
                else:
                    bibliography_entries.append(f"[{i}] {cit['type'].title()}: {cit['citation']}")

            bibliography_section = "\n\n## References\n" + "\n".join(bibliography_entries)
            # Remove original citations and add bibliography
            # Simple approach: just append bibliography (in reality we'd remove inline citations)
            formatted_content = content + bibliography_section
            citation_text = f"Moved {len(citations)} citations to bibliography section"

        elif citation_format == "apa":
            # APA-style formatting (simplified)
            apa_entries = []
            for i, cit in enumerate(citations, 1):
                if cit["type"] == "transcript":
                    apa_entries.append(f"Transcript segment {cit['citation']}.")
                elif cit["type"] == "slide":
                    apa_entries.append(f"Slide {cit['citation']}.")
                elif cit["type"] == "lesson":
                    apa_entries.append(f"Lesson material {cit['citation']}.")
                else:
                    apa_entries.append(f"{cit['type'].title()} {cit['citation']}.")

            formatted_content = content  # Keep inline for simplicity in this implementation
            citation_text = f"Formatted {len(citations)} citations in APA style (inline)"

        elif citation_format == "mla":
            # MLA-style formatting (simplified)
            mla_entries = []
            for i, cit in enumerate(citations, 1):
                if cit["type"] == "transcript":
                    mla_entries.append(f"Transcript segment {cit['citation']}.")
                elif cit["type"] == "slide":
                    mla_entries.append(f"Slide {cit['citation']}.")
                elif cit["type"] == "lesson":
                    mla_entries.append(f"Lesson material {cit['citation']}.")
                else:
                    mla_entries.append(f"{cit['type'].title()} {cit['citation']}.")

            formatted_content = content  # Keep inline for simplicity
            citation_text = f"Formatted {len(citations)} citations in MLA style (inline)"

        else:
            return {
                "error": "invalid_format",
                "message": f"Unsupported citation format: {citation_format}",
                "valid_formats": ["inline", "bibliography", "apa", "mla"]
            }

        return {
            "formatted_content": formatted_content,
            "citations": citations,
            "citation_format": citation_format,
            "message": citation_text
        }

    def _validate_citations(self, content: str) -> Dict[str, Any]:
        """Validate citations in content."""
        extraction_result = self._extract_citations(content)
        citations = extraction_result.get("citations", [])

        validation_results = []
        issues = []

        for cit in citations:
            is_valid = True
            issues_for_this_citation = []

            # Validate transcript citations
            if cit["type"] == "transcript":
                citation_str = cit["citation"]
                # Check format [Txx-NNN]
                if not re.match(r'\[T\d{2}-\d{3}\]$', citation_str):
                    is_valid = False
                    issues_for_this_citation.append("Invalid transcript citation format")
                else:
                    # Extract numbers and validate ranges
                    match = re.match(r'\[T(\d{2})-(\d{3})\]', citation_str)
                    if match:
                        day_num = int(match.group(1))
                        segment_num = int(match.group(2))
                        if day_num < 1 or day_num > 6:
                            is_valid = False
                            issues_for_this_citation.append("Day number out of range (01-06)")
                        if segment_num < 1 or segment_num > 999:  # Assuming max 999 segments
                            is_valid = False
                            issues_for_this_citation.append("Segment number out of reasonable range")

            # Validate slide citations
            elif cit["type"] == "slide":
                try:
                    slide_num = int(cit["citation"])
                    if slide_num < 1:
                        is_valid = False
                        issues_for_this_citation.append("Slide number must be positive")
                except ValueError:
                    is_valid = False
                    issues_for_this_citation.append("Slide citation must be a number")

            # Validate lesson citations
            elif cit["type"] == "lesson":
                lesson_str = cit["citation"]
                if not re.match(r'day\d+(?:-[a-zA-Z0-9]+)?', lesson_str):
                    is_valid = False
                    issues_for_this_citation.append("Invalid lesson reference format")

            validation_results.append({
                "citation": cit,
                "valid": is_valid,
                "issues": issues_for_this_citation
            })

            if not is_valid:
                issues.extend(issues_for_this_citation)

        if not citations:
            message = "No citations found to validate"
            valid_count = 0
        else:        # Otherwise, use the found citations count
            valid_count = len([c for c in validation_results if c["valid"]])

        # Create summary message
        if not citations:
            message = "No citations found to validate"
        elif len(issues) == 0:
            message = f"All {len(citations)} citations are valid"
        else:
            message = f"Found {len(issues)} validation issues in {len(citations)} citations"

        return {
            "citations": citations,
            "validation_results": validation_results,
            "valid_count": valid_count,
            "total_count": len(citations),
            "issues": list(set(issues)),  # Remove duplicate issues
            "message": message
        }