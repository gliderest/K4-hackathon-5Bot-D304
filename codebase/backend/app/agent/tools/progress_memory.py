from backend.app.memory.progress_store import ProgressStore
from backend.app.schemas.progress import ProgressPatch, ProgressSnapshot


async def read_learning_memory(
    store: ProgressStore,
    learner_id: str,
    course_id: str,
) -> str:
    return await store.build_context(learner_id, course_id)


async def save_learning_progress(
    store: ProgressStore,
    learner_id: str,
    patch: ProgressPatch,
) -> ProgressSnapshot:
    return await store.update(learner_id, patch)

