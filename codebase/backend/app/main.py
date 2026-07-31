from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api.router import api_router
from backend.app.core.config import settings
from backend.app.core.runtime import runtime


@asynccontextmanager
async def lifespan(_: FastAPI):
    await runtime.initialize()
    yield


app = FastAPI(
    title="VLearn Cross-Lesson AI Tutor",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.mount(
    "/api/assets/slides",
    StaticFiles(directory=settings.resolve_path(settings.slides_dir)),
    name="slides",
)
app.mount(
    "/api/assets/transcripts",
    StaticFiles(directory=settings.resolve_path(settings.transcripts_dir)),
    name="transcripts",
)
app.mount(
    "/api/assets/uploads",
    StaticFiles(directory=settings.resolve_path(settings.user_upload_dir)),
    name="uploads",
)
