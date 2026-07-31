"""OpenAI-compatible model gateway used by the tool-calling tutor agent."""

import asyncio
from pathlib import Path
from typing import Any

from openai import APIStatusError, OpenAI

from backend.app.core.config import Settings


OPENAI_COMPATIBLE_PROVIDERS = {
    "openai",
    "openrouter",
    "shopaikey",
    "openai_compatible",
    "openai-compatible",
    "custom",
}


class AgentModelGateway:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.provider = settings.ai_provider.strip().casefold()
        self.enabled = (
            self.provider in OPENAI_COMPATIBLE_PROVIDERS
            and bool(settings.ai_api_key)
            and bool(settings.ai_model)
        )
        self.system_prompt = self._load_system_prompt(settings.system_prompt_path)
        self._client = self._build_client() if self.enabled else None

    def _load_system_prompt(self, configured_path: str) -> str:
        prompt_path = Path(configured_path)
        if not prompt_path.is_absolute():
            project_root = Path(__file__).resolve().parents[3]
            prompt_path = project_root / prompt_path
        if not prompt_path.is_file():
            raise FileNotFoundError(f"Không tìm thấy system prompt: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8").strip()

    def _build_client(self) -> OpenAI:
        kwargs: dict[str, str] = {"api_key": self.settings.ai_api_key}
        base_url = self._resolve_base_url()
        if base_url:
            kwargs["base_url"] = base_url
        return OpenAI(**kwargs)

    def _resolve_base_url(self) -> str:
        if self.settings.ai_base_url.strip():
            return self.settings.ai_base_url.strip()
        if self.provider == "openrouter":
            return "https://openrouter.ai/api/v1"
        if self.provider == "shopaikey":
            return "https://api.shopaikey.com/v1"
        return ""

    async def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> Any:
        if not self.enabled or self._client is None:
            raise RuntimeError(
                "Agent LLM chưa được cấu hình. Hãy kiểm tra AI_PROVIDER, AI_MODEL, AI_API_KEY và AI_BASE_URL."
            )
        return await asyncio.to_thread(self._complete_sync, messages, tools)

    def _complete_sync(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> Any:
        assert self._client is not None
        max_tokens = max(128, min(self.settings.agent_max_tokens, 1200))
        try:
            response = self._create_completion(messages, tools, max_tokens)
        except APIStatusError as error:
            # OpenRouter returns 402 when the requested output reservation is
            # larger than the remaining key/credit limit. Retry once with a
            # compact response budget before surfacing the provider error.
            if error.status_code != 402 or max_tokens <= 256:
                raise
            response = self._create_completion(messages, tools, 256)
        return response.choices[0].message

    def _create_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int,
    ) -> Any:
        assert self._client is not None
        payload: dict[str, Any] = {
            "model": self.settings.ai_model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        return self._client.chat.completions.create(**payload)

    @staticmethod
    def user_facing_error(error: Exception) -> str:
        if isinstance(error, APIStatusError):
            if error.status_code == 401:
                return "API key của mô hình AI không hợp lệ hoặc đã hết hiệu lực."
            if error.status_code == 402:
                error_text = str(error)
                if "Prompt tokens limit exceeded" in error_text:
                    return (
                        "Prompt gửi sang AI provider vẫn còn quá dài so với giới hạn key OpenRouter. "
                        "Hãy rút ngắn câu hỏi/tài liệu đang mở, hoặc tăng limit của key."
                    )
                return (
                    "Tài khoản AI provider không đủ credit hoặc key đang giới hạn chi phí. "
                    "Hãy nạp thêm credit hoặc giảm AGENT_MAX_TOKENS."
                )
            if error.status_code == 429:
                return "AI provider đang giới hạn tần suất gọi. Bạn hãy thử lại sau ít phút."
        return "Mình chưa thể kết nối tới mô hình AI. Bạn hãy thử lại sau."
