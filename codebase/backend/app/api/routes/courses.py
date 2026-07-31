from fastapi import APIRouter, HTTPException

from backend.app.core.runtime import runtime
from backend.app.schemas.course import CourseOutlineResponse, LessonDetailResponse


router = APIRouter()


@router.get("/{course_id}/outline", response_model=CourseOutlineResponse)
async def get_outline(course_id: str, learner_id: str) -> CourseOutlineResponse:
    return await runtime.course_service.get_outline(course_id=course_id, learner_id=learner_id)


@router.get("/{course_id}/lessons/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(course_id: str, lesson_id: str) -> LessonDetailResponse:
    if lesson_id not in runtime.corpus.lessons:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return await runtime.course_service.get_lesson(course_id=course_id, lesson_id=lesson_id)
