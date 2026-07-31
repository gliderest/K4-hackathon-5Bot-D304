from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    frontend_origin: str = "http://localhost:5173"

    ai_provider: str = "local"
    ai_model: str = ""
    ai_api_key: str = ""
    ai_base_url: str = ""
    system_prompt_path: str = "./prompts/system-prompt.md"
    agent_max_tokens: int = 250
    embedding_provider: str = ""
    embedding_model: str = ""
    embedding_api_key: str = ""
    embedding_base_url: str = ""
    embedding_batch_size: int = 64

    web_search_provider: str = "tavily"
    web_search_api_key: str = ""
    web_search_max_results: int = 5
    web_search_timeout_seconds: float = 12.0
    web_search_fallback_min_score: float = 0.7

    course_id: str = "vlearn-hackathon"
    course_title: str = "VLearn Cross-Lesson AI Tutor"
    course_data_root: str = "./data/vlearn-pack"
    slides_dir: str = "./data/vlearn-pack/slides"
    transcripts_dir: str = "./data/vlearn-pack/transcript"
    vector_store_dir: str = "./data/vector_store"
    chunks_dir: str = "./data/processed/chunks"
    rag_top_k: int = 6
    rag_min_score: float = 0.18

    database_url: str = "sqlite+aiosqlite:///./storage/vlearn.db"
    user_upload_dir: str = "./data/user_uploads"
    additional_documents_dir: str = "./data/additional_documents"
    pending_additional_documents_dir: str = "./data/pending_additional_documents"
    max_upload_mb: int = 20

    def resolve_path(self, value: str) -> Path:
        return Path(value).resolve()

    @property
    def database_path(self) -> Path:
        raw = self.database_url.removeprefix("sqlite+aiosqlite:///")
        return Path(raw).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
