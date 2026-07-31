from __future__ import annotations

import os
from typing import Any

import openai

# Add the project root to sys.path so we can import from agents.base
import sys
from pathlib import Path

# Get the project root (assuming this file is in test/providers/)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # Go up two levels: providers -> test

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now we can import from agents.base
from agents.tool_registry import ToolCall
from .base import ModelResponse, Provider


class OpenRouterProvider:
    def __init__(self) -> None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.default_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        model_to_use = model or self.default_model

        candidate_models = [
            model_to_use,
            "openai/gpt-4o-mini",
            "google/gemini-2.5-flash",
            "anthropic/claude-3-haiku",
            "deepseek/deepseek-chat",
        ]
        # Preserve order while removing duplicates
        seen = set()
        unique_candidates = []
        for m in candidate_models:
            if m not in seen:
                seen.add(m)
                unique_candidates.append(m)

        last_error = None
        for candidate in unique_candidates:
            params: dict[str, Any] = {
                "model": candidate,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": int(os.getenv("MAX_TOKENS", "2048")),
            }

            if tools is not None:
                params["tools"] = [{"type": "function", "function": tool} for tool in tools]
                if tool_choice is not None:
                    params["tool_choice"] = tool_choice

            params = {k: v for k, v in params.items() if v is not None}

            try:
                response = self.client.chat.completions.create(**params)

                tool_calls = []
                if response.choices[0].message.tool_calls is not None:
                    for tool_call in response.choices[0].message.tool_calls:
                        args = tool_call.function.arguments
                        if isinstance(args, str):
                            import json
                            try:
                                args = json.loads(args)
                            except json.JSONDecodeError:
                                pass
                        tool_calls.append(
                            ToolCall(
                                name=tool_call.function.name,
                                args=args,
                            )
                        )

                return ModelResponse(
                    text=response.choices[0].message.content,
                    tool_calls=tool_calls,
                    raw=response,
                )
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise last_error