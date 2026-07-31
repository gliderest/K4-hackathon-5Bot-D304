from backend.app.rag.citation import citation_from_hit
from backend.app.rag.contracts import SearchHit
from backend.app.schemas.chat import Citation


def build_source_links(hits: list[SearchHit]) -> list[Citation]:
    return [citation_from_hit(hit) for hit in hits]

