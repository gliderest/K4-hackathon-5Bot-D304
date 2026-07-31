from backend.app.rag.contracts import SearchHit
from backend.app.rag.retriever import Retriever


async def course_search(
    retriever: Retriever,
    query: str,
    course_id: str,
    top_k: int,
) -> list[SearchHit]:
    return await retriever.search_course(query=query, course_id=course_id, top_k=top_k)

