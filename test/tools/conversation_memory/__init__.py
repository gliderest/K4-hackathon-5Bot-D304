from __future__ import annotations

from .conversation_memory import ConversationMemoryTool

# Make the tool class available for import
__all__ = ["ConversationMemoryTool"]

# Create an instance for easy importing
conversation_memory_tool = ConversationMemoryTool()