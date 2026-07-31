from backend.app.agent.tutor_agent import TutorAgent
from backend.app.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    def __init__(self, agent: TutorAgent) -> None:
        self.agent = agent

    async def answer(self, request: ChatRequest) -> ChatResponse:
        return await self.agent.run(request)
