from backend.app.rag.contracts import SearchHit
from backend.app.schemas.chat import Citation


def build_citation(hit: SearchHit) -> Citation:
    chunk = hit.chunk
    if chunk.source_type == "slide":
        suffix = f"#page={chunk.page}" if chunk.page else ""
        viewer_path = f"/api/assets/slides/{chunk.source_file}{suffix}"
        label = f"{chunk.title} - slide {chunk.page}"
    elif chunk.source_type == "transcript":
        suffix = f"#segment={chunk.segment_id}" if chunk.segment_id else ""
        viewer_path = f"/api/assets/transcripts/{chunk.source_file}{suffix}"
        label = f"{chunk.title} - {chunk.segment_id or 'segment'}"
    else:
        owner = chunk.owner_learner_id or "shared"
        conversation_id = chunk.metadata.get("conversation_id")
        viewer_path = (
            f"/api/assets/uploads/{owner}/{conversation_id}/{chunk.source_file}"
            if conversation_id
            else f"/api/assets/uploads/{owner}/{chunk.source_file}"
        )
        label = f"{chunk.title} - tài liệu người học"

    return Citation(
        label=label,
        source_type=chunk.source_type,
        source_id=chunk.source_file,
        lesson_id=chunk.lesson_id,
        page=chunk.page,
        segment_id=chunk.segment_id,
        viewer_path=viewer_path,
        score=round(hit.score, 3),
    )
