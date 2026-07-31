from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.tool_registry import Tool


class ConversationMemoryTool(Tool):
    """
    Tool for retrieving and managing conversation history with the student.
    Provides capabilities to search past conversations, get recent exchanges,
    and summarize conversation history.
    """

    name: str = "conversation_memory"
    description: str = "Retrieve and summarize previous conversations with the student"

    def __init__(self, data_dir: str = "./conversation_data") -> None:
        super().__init__()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.conversations_file = self.data_dir / "conversations.json"
        self.load_conversations()

    def load_conversations(self) -> None:
        """Load conversations from storage."""
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.conversations = []
        else:
            self.conversations = []

    def save_conversations(self) -> None:
        """Save conversations to storage."""
        try:
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, indent=2, ensure_ascii=False)
        except IOError as e:
            # In a real application, we'd log this error
            pass

    def add_conversation(
        self,
        student_id: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a conversation exchange to memory.

        Args:
            student_id: Identifier for the student
            user_message: The student's message
            agent_response: The agent's response
            metadata: Additional metadata (timestamp, topic, etc.)
        """
        conversation_entry = {
            "student_id": student_id,
            "user_message": user_message,
            "agent_response": agent_response,
            "timestamp": self._get_timestamp(),
            "metadata": metadata or {}
        }
        self.conversations.append(conversation_entry)
        self.save_conversations()

    def execute(
        self,
        operation: str = "search",
        query: str = "",
        student_id: str = "default_student",
        limit: int = 10,
        topic: str = "",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute operations on conversation memory.

        Args:
            operation: Operation to perform (search, get_recent, get_by_topic, get_summary)
            query: Search query (for search operation)
            student_id: Student identifier to filter conversations
            limit: Maximum number of results to return
            topic: Topic to filter by (for get_by_topic operation)
            **kwargs: Additional arguments

        Returns:
            Dict containing the results of the operation
        """
        try:
            if operation == "search":
                return self._search_conversations(query, student_id, limit)
            elif operation == "get_recent":
                return self._get_recent_conversations(student_id, limit)
            elif operation == "get_by_topic":
                return self._get_conversations_by_topic(topic, student_id, limit)
            elif operation == "get_summary":
                return self._get_conversation_summary(student_id, limit)
            else:
                return {
                    "error": "invalid_operation",
                    "message": f"Unknown operation: {operation}",
                    "valid_operations": ["search", "get_recent", "get_by_topic", "get_summary"]
                }
        except Exception as e:
            return {
                "error": type(e).__name__,
                "message": f"Error accessing conversation memory: {str(e)}",
                "operation": operation
            }

    def _search_conversations(self, query: str, student_id: str, limit: int) -> Dict[str, Any]:
        """Search conversations by query text."""
        if not query:
            return self._get_recent_conversations(student_id, limit)

        query_lower = query.lower()
        matching_conversations = []

        for conv in self.conversations:
            if conv.get("student_id") == student_id:
                user_msg = conv.get("user_message", "").lower()
                agent_resp = conv.get("agent_response", "").lower()
                if query_lower in user_msg or query_lower in agent_resp:
                    matching_conversations.append(conv)

        # Sort by timestamp (most recent first)
        matching_conversations.sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

        return {
            "operation": "search",
            "query": query,
            "student_id": student_id,
            "results": matching_conversations[:limit],
            "total_found": len(matching_conversations),
            "message": f"Found {len(matching_conversations[:limit])} conversations matching '{query}'"
        }

    def _get_recent_conversations(self, student_id: str, limit: int) -> Dict[str, Any]:
        """Get recent conversations for a student."""
        student_conversations = [
            conv for conv in self.conversations
            if conv.get("student_id") == student_id
        ]

        # Sort by timestamp (most recent first)
        student_conversations.sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

        return {
            "operation": "get_recent",
            "student_id": student_id,
            "results": student_conversations[:limit],
            "total_found": len(student_conversations),
            "message": f"Retrieved {len(student_conversations[:limit])} recent conversations"
        }

    def _get_conversations_by_topic(self, topic: str, student_id: str, limit: int) -> Dict[str, Any]:
        """Get conversations by topic (simplified implementation)."""
        # In a real implementation, we'd have topic tagging
        # For now, we'll search in the conversation content
        if not topic:
            return self._get_recent_conversations(student_id, limit)

        topic_lower = topic.lower()
        matching_conversations = []

        for conv in self.conversations:
            if conv.get("student_id") == student_id:
                user_msg = conv.get("user_message", "").lower()
                agent_resp = conv.get("agent_response", "").lower()
                if topic_lower in user_msg or topic_lower in agent_resp:
                    matching_conversations.append(conv)

        # Sort by timestamp (most recent first)
        matching_conversations.sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

        return {
            "operation": "get_by_topic",
            "topic": topic,
            "student_id": student_id,
            "results": matching_conversations[:limit],
            "total_found": len(matching_conversations),
            "message": f"Found {len(matching_conversations[:limit])} conversations about '{topic}'"
        }

    def _get_conversation_summary(self, student_id: str, limit: int) -> Dict[str, Any]:
        """Get a summary of conversation history."""
        student_conversations = [
            conv for conv in self.conversations
            if conv.get("student_id") == student_id
        ]

        if not student_conversations:
            return {
                "operation": "get_summary",
                "student_id": student_id,
                "summary": "No conversation history found.",
                "total_conversations": 0,
                "message": "No conversation history available for summary."
            }

        # Sort by timestamp (most recent first)
        student_conversations.sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

        recent_conversations = student_conversations[:limit]

        # Create a simple summary
        topics_mentioned = set()
        question_types = set()

        for conv in recent_conversations:
            # Simple topic extraction (in reality, we'd use NLP)
            user_msg = conv.get("user_message", "").lower()
            # Extract potential topics (words longer than 4 chars that aren't common words)
            words = [w.strip(".,!?;:") for w in user_msg.split()]
            for word in words:
                if len(word) > 4 and word not in {
                    "what", "when", "where", "which", "while", "about", "would", "could", "should",
                    "there", "their", "these", "those", "through", "shall", "because"
                }:
                    topics_mentioned.add(word)

            # Detect question types
            if any(word in user_msg for word in ["what", "who", "where", "when", "why", "how"]):
                question_types.add("question")
            if any(word in user_msg for word in ["explain", "describe", "tell"]):
                question_types.add("explanation_request")
            if any(word in user_msg for word in ["compare", "difference", "versus", "vs"]):
                question_types.add("comparison")
            if any(word in user_msg for word in ["summarize", "summary", "brief"]):
                question_types.add("summarization_request")

        summary_parts = [
            f"Conversation summary for student {student_id}:",
            f"- Total conversations: {len(student_conversations)}",
            f"- Recent conversations analyzed: {len(recent_conversations)}",
        ]

        if topics_mentioned:
            topics_list = list(topics_mentioned)[:10]  # Limit to top 10
            summary_parts.append(f"- Topics mentioned: {', '.join(sorted(topics_list))}")

        if question_types:
            summary_parts.append(f"- Question types: {', '.join(sorted(question_types))}")

        # Add recent conversation snippets
        if recent_conversations:
            summary_parts.append("- Recent conversation snippets:")
            for i, conv in enumerate(recent_conversations[:3], 1):
                user_msg = conv.get("user_message", "")[:100]
                agent_resp = conv.get("agent_response", "")[:100]
                if len(conv.get("user_message", "")) > 100:
                    user_msg += "..."
                if len(conv.get("agent_response", "")) > 100:
                    agent_resp += "..."
                summary_parts.append(f"  {i}. Student: {user_msg}")
                summary_parts.append(f"     Agent: {agent_resp}")

        return {
            "operation": "get_summary",
            "student_id": student_id,
            "summary": "\n".join(summary_parts),
            "total_conversations": len(student_conversations),
            "recent_analyzed": len(recent_conversations),
            "topics_mentioned": list(topics_mentioned),
            "question_types": list(question_types),
            "message": f"Generated summary of {len(student_conversations)} conversations"
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()