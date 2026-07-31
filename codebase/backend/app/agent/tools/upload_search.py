from backend.app.rag.contracts import SearchHit
from backend.app.rag.retriever import Retriever


async def upload_search(
    retriever: Retriever,
    query: str,
    learner_id: str,
    document_ids: list[str],
    top_k: int,
) -> list[SearchHit]:
    """Bắt buộc filter theo learner_id để không lẫn dữ liệu giữa học viên."""
    return await retriever.search_uploads(
        query=query,
        learner_id=learner_id,
        document_ids=document_ids,
        top_k=top_k,
    )

