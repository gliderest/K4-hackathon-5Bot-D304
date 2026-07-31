from backend.app.agent.tutor_agent import TutorAgent
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.memory.chat_history_store import SqliteChatHistoryStore


class ChatService:
    def __init__(self, agent: TutorAgent, history_store: SqliteChatHistoryStore) -> None:
        self.agent = agent
        self.history_store = history_store

    async def answer(self, request: ChatRequest) -> ChatResponse:
        conversation_id = await self.history_store.get_or_create(
            learner_id=request.learner_id,
            course_id=request.course_id,
            first_message=request.message,
            conversation_id=request.conversation_id,
        )
        await self.history_store.append_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
        )
        response = await self.agent.run(request)
        response = response.model_copy(update={"conversation_id": conversation_id})
        await self.history_store.append_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response.answer,
            citations=response.citations,
        )
        return response
