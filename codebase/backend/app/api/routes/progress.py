from fastapi import APIRouter

from backend.app.core.runtime import runtime
from backend.app.schemas.progress import ProgressPatch, ProgressSnapshot


router = APIRouter()


@router.get("/{learner_id}", response_model=ProgressSnapshot)
async def get_progress(learner_id: str, course_id: str) -> ProgressSnapshot:
    return await runtime.progress_store.get(learner_id=learner_id, course_id=course_id)


@router.patch("/{learner_id}", response_model=ProgressSnapshot)
async def patch_progress(
    learner_id: str,
    patch: ProgressPatch,
) -> ProgressSnapshot:
    return await runtime.progress_store.update(learner_id=learner_id, patch=patch)
