from fastapi import APIRouter

from backend.app.api.routes import chat, courses, progress, uploads


api_router = APIRouter()


@api_router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
