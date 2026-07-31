from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

# Import tool implementations will go here as we create them
# For now, we'll define the structure

TOOL_FUNCTIONS: Dict[str, Any] = {}


def load_tool_declarations(path: Path) -> List[Dict[str, Any]]:
    """Load tool declarations from YAML file."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert tool declarations to OpenAI function calling format."""
    return [{
        "type": "function",
        "function": {
            "name": item["name"],
            "description": item.get("description", ""),
            "parameters": item.get("parameters", {"type": "object", "properties": {}}),
        },
    } for item in declarations]