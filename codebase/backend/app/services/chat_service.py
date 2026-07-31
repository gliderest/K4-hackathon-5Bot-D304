import asyncio
import json
from collections.abc import AsyncIterator

from backend.app.agent.tutor_agent import TutorAgent
from backend.app.schemas.chat import (
    ChatHistoryMessage,
    ChatRequest,
    ChatResponse,
    ToolTraceEvent,
)
from backend.app.memory.chat_history_store import SqliteChatHistoryStore


HISTORY_MESSAGE_LIMIT = 12
HISTORY_CHAR_LIMIT = 2600
HISTORY_ITEM_CHAR_LIMIT = 520


class ChatService:
    def __init__(self, agent: TutorAgent, history_store: SqliteChatHistoryStore) -> None:
        self.agent = agent
        self.history_store = history_store

    async def answer(self, request: ChatRequest) -> ChatResponse:
        conversation_id, prepared_request = await self._prepare_request(request)
        response = await self.agent.run(prepared_request)
        return await self._finish_response(conversation_id, response)

    async def stream_answer(self, request: ChatRequest) -> AsyncIterator[str]:
        """Send tool activity first, then the final answer as Server-Sent Events."""
        conversation_id, prepared_request = await self._prepare_request(request)
        events: asyncio.Queue[tuple[str, dict]] = asyncio.Queue()

        async def on_trace(event: ToolTraceEvent) -> None:
            await events.put(("tool_trace", event.model_dump(mode="json")))

        async def produce() -> None:
            try:
                response = await self.agent.run(prepared_request, on_trace=on_trace)
                response = await self._finish_response(conversation_id, response)
                await events.put(("answer", response.model_dump(mode="json")))
            except Exception as error:  # The client cannot receive an HTTP error after streaming starts.
                await events.put(("error", {"detail": str(error)}))

        task = asyncio.create_task(produce())
        try:
            while True:
                event_name, payload = await events.get()
                yield self._as_sse(event_name, payload)
                if event_name in {"answer", "error"}:
                    break
        finally:
            if not task.done():
                task.cancel()

    async def _prepare_request(self, request: ChatRequest) -> tuple[str, ChatRequest]:
        conversation_id = await self.history_store.get_or_create(
            learner_id=request.learner_id,
            course_id=request.course_id,
            first_message=request.message,
            conversation_id=request.conversation_id,
        )
        conversation = await self.history_store.get_conversation(
            conversation_id,
            request.learner_id,
            request.course_id,
        )
        conversation_history = self._compact_history(conversation.messages if conversation else [])
        await self.history_store.append_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
        )
        return conversation_id, request.model_copy(
            update={
                "conversation_id": conversation_id,
                "conversation_history": conversation_history,
            }
        )

    async def _finish_response(
        self,
        conversation_id: str,
        response: ChatResponse,
    ) -> ChatResponse:
        response = response.model_copy(update={"conversation_id": conversation_id})
        await self.history_store.append_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response.answer,
            citations=response.citations,
            tool_trace=response.tool_trace,
        )
        return response

    @staticmethod
    def _as_sse(event_name: str, payload: dict) -> str:
        return f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    @staticmethod
    def _compact_history(messages: list) -> list[ChatHistoryMessage]:
        selected: list[ChatHistoryMessage] = []
        remaining = HISTORY_CHAR_LIMIT

        for message in reversed(messages[-HISTORY_MESSAGE_LIMIT:]):
            content = " ".join(str(message.content).split()).strip()
            if not content:
                continue
            if len(content) > HISTORY_ITEM_CHAR_LIMIT:
                content = content[:HISTORY_ITEM_CHAR_LIMIT].rsplit(" ", 1)[0].strip() + "..."
            if len(content) > remaining:
                if selected:
                    break
                content = content[:remaining].rsplit(" ", 1)[0].strip() + "..."
            selected.append(ChatHistoryMessage(role=message.role, content=content))
            remaining -= len(content)
            if remaining <= 0:
                break

        return list(reversed(selected))
