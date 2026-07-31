from __future__ import annotations

from typing import Any, Dict, Optional, Type
from .base import ToolCall


class Tool:
    """Base class for all tools in the AI Learning Agent system."""

    name: str = ""
    description: str = ""

    def __init__(self) -> None:
        if not self.name:
            raise ValueError("Tool must have a name")
        if not self.description:
            raise ValueError("Tool must have a description")

    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the tool with the given arguments.

        Args:
            **kwargs: Arguments for the tool execution

        Returns:
            Any: Result of the tool execution
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def get_definition(self) -> Dict[str, Any]:
        """
        Get the tool definition in the format expected by the LLM.

        Returns:
            Dict[str, Any]: Tool definition for LLM function calling
        """
        # This would typically be loaded from the tools.yaml file
        # For now, returning a basic structure
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }


class ToolRegistry:
    """
    Registry for managing tools in the AI Learning Agent.
    The agent never directly calls tools - it always goes through the registry.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}
        self._tool_classes: Dict[str, Type[Tool]] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool instance.

        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool

    def register_class(self, tool_class: Type[Tool]) -> None:
        """
        Register a tool class (for lazy instantiation).

        Args:
            tool_class: Tool class to register
        """
        # Create an instance to get the name
        temp_instance = tool_class()
        self._tool_classes[temp_instance.name] = tool_class

    def get(self, name: str) -> Optional[Tool]:
        """
        Get a tool instance by name.

        Args:
            name: Name of the tool to retrieve

        Returns:
            Tool: The tool instance, or None if not found
        """
        # Check if we have an instance already
        if name in self._tools:
            return self._tools[name]

        # Check if we have a class we can instantiate
        if name in self._tool_classes:
            tool_instance = self._tool_classes[name]()
            self._tools[name] = tool_instance  # Cache the instance
            return tool_instance

        return None

    def exists(self, name: str) -> bool:
        """
        Check if a tool exists in the registry.

        Args:
            name: Name of the tool to check

        Returns:
            bool: True if the tool exists, False otherwise
        """
        return name in self._tools or name in self._tool_classes

    def list_tools(self) -> List[str]:
        """
        Get a list of all registered tool names.

        Returns:
            List[str]: List of tool names
        """
        return list(set(list(self._tools.keys()) + list(self._tool_classes.keys())))

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get definitions for all registered tools.

        Returns:
            List[Dict[str, Any]]: List of tool definitions for LLM
        """
        definitions = []
        for name in self.list_tools():
            tool = self.get(name)
            if tool:
                definitions.append(tool.get_definition())
        return definitions