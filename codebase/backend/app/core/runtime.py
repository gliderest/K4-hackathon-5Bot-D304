from backend.app.agent.tutor_agent import TutorAgent
from backend.app.core.config import settings
from backend.app.memory.progress_store import SqliteProgressStore
from backend.app.memory.chat_history_store import SqliteChatHistoryStore
from backend.app.rag.embeddings import OpenAIEmbeddingService
from backend.app.rag.ingestion import CourseCorpus
from backend.app.rag.retriever import LocalRetriever
from backend.app.services.chat_service import ChatService
from backend.app.services.course_service import CourseService
from backend.app.services.upload_service import UploadService
from backend.app.services.document_writer import CurrentDocumentWriter
from backend.app.tools.search_document import SearchDocumentTool
from backend.app.tools.analyse_current_document import AnalyseCurrentDocumentTool


class AppRuntime:
    def __init__(self) -> None:
        self.embedding_service = OpenAIEmbeddingService(settings)
        self.corpus = CourseCorpus(settings, embedding_service=self.embedding_service)
        self.progress_store = SqliteProgressStore(settings.database_path)
        self.chat_history_store = SqliteChatHistoryStore(settings.database_path)
        self.retriever = LocalRetriever(
            settings,
            self.corpus,
            embedding_service=self.embedding_service,
        )
        self.upload_service = UploadService(
            settings,
            embedding_service=self.embedding_service,
        )
        self.agent = TutorAgent(
            search_document=SearchDocumentTool(retriever=self.retriever),
            analyse_current_document=AnalyseCurrentDocumentTool(retriever=self.retriever),
            current_document_writer=CurrentDocumentWriter(settings),
            progress_store=self.progress_store,
        )
        self.chat_service = ChatService(agent=self.agent, history_store=self.chat_history_store)
        self.course_service = CourseService(
            settings=settings,
            corpus=self.corpus,
            progress_store=self.progress_store,
        )

    async def initialize(self) -> None:
        settings.resolve_path(settings.user_upload_dir).mkdir(parents=True, exist_ok=True)
        settings.resolve_path(settings.chunks_dir).mkdir(parents=True, exist_ok=True)
        settings.resolve_path(settings.vector_store_dir).mkdir(parents=True, exist_ok=True)
        await self.corpus.build()
        await self.progress_store.initialize()
        await self.chat_history_store.initialize()


runtime = AppRuntime()
