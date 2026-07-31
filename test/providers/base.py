from __future__ import annotations

from typing import Any, Protocol, List, Dict, Optional


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


# ModelResponse would be defined elsewhere or imported
# For now, we'll define a simple version to avoid circular imports
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelResponse:
    text: str | None = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    raw: Any | None = None