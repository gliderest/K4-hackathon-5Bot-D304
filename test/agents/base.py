from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, List, Dict, Optional


@dataclass
class ToolCall:
    name: str
    args: Dict[str, Any]


@dataclass
class ModelResponse:
    text: str | None = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    raw: Any | None = None


@dataclass
class AgentState:
    """State of the agent during execution."""
    messages: List[Dict[str, str]] = field(default_factory=list)
    intent: Optional[Dict[str, Any]] = None
    plan: Any = None
    context: str = ""
    response: str | None = None
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    reflection: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None


class Provider(Protocol):
    def complete(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        """Return normalized text/tool calls regardless of vendor API shape."""
        ...


@dataclass
class AgentRun:
    text: str | None = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    state: AgentState | None = None  # <--- ADD THIS LINE


class LearningAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        system_prompt: str,
        tools: List[Dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model = model

    def run(self, user_messages: List[Dict[str, str]], *, tool_choice: Any | None = None) -> AgentRun:
        messages = [{"role": "system", "content": self.system_prompt}, *user_messages]
        response = self.provider.complete(
            messages,
            self.tools,
            model=self.model,
            temperature=0.0,
            tool_choice=tool_choice,
        )
        results: List[Dict[str, Any]] = []
        for call in response.tool_calls:
            # Tool execution will be handled by the tool registry/executor
            results.append({"tool": call.name, "args": call.args, "result": None})  # Placeholder
        return AgentRun(text=response.text, tool_calls=response.tool_calls, tool_results=results)