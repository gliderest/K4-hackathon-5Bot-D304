from fastapi import APIRouter

from backend.app.core.runtime import runtime
from backend.app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await runtime.chat_service.answer(request)
