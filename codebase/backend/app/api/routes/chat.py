from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from backend.app.core.runtime import runtime
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.schemas.conversation import ConversationDetail, ConversationSummary


router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        return await runtime.chat_service.answer(request)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/stream")
async def stream_chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        runtime.chat_service.stream_answer(request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/history", response_model=list[ConversationSummary])
async def list_history(
    learner_id: str = Query(...),
    course_id: str = Query(...),
) -> list[ConversationSummary]:
    return await runtime.chat_history_store.list_conversations(learner_id, course_id)


@router.get("/history/{conversation_id}", response_model=ConversationDetail)
async def get_history(
    conversation_id: str,
    learner_id: str = Query(...),
    course_id: str = Query(...),
) -> ConversationDetail:
    conversation = await runtime.chat_history_store.get_conversation(
        conversation_id, learner_id, course_id
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc hội thoại.")
    return conversation
