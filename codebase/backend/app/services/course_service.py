from backend.app.core.config import Settings
from backend.app.memory.progress_store import SqliteProgressStore
from backend.app.rag.ingestion import CourseCorpus
from backend.app.schemas.course import (
    CourseLesson,
    CourseOutlineResponse,
    CourseSlide,
    LessonDetailResponse,
)


def transcript_body(markdown: str) -> str:
    """Remove the source/convention/processing notes before the lesson body."""
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("## "):
            return "\n".join(lines[index:]).strip()
    return markdown.strip()


class CourseService:
    def __init__(
        self,
        settings: Settings,
        corpus: CourseCorpus,
        progress_store: SqliteProgressStore,
    ) -> None:
        self.settings = settings
        self.corpus = corpus
        self.progress_store = progress_store

    async def get_outline(self, course_id: str, learner_id: str) -> CourseOutlineResponse:
        progress = await self.progress_store.get(learner_id=learner_id, course_id=course_id)
        completion_map = {
            lesson.lesson_id: lesson.completion_percent for lesson in progress.lessons
        }
        lessons = [
            CourseLesson(
                lesson_id=lesson.lesson_id,
                title=lesson.title,
                transcript_file=lesson.transcript_file,
                slide_file=lesson.source_slide_file,
                slide_viewer_path=(
                    f"/api/assets/slides/{lesson.source_slide_file}"
                    if lesson.source_slide_file
                    else None
                ),
                segment_count=len(lesson.segment_ids),
                completion_percent=completion_map.get(lesson.lesson_id, 0),
            )
            for lesson in self.corpus.lessons.values()
        ]
        slides = [
            CourseSlide(
                slide_id=slide["slide_id"],
                title=slide["title"],
                slide_file=slide["slide_file"],
                slide_viewer_path=f"/api/assets/slides/{slide['slide_file']}",
            )
            for slide in self.corpus.slide_documents
        ]
        return CourseOutlineResponse(
            course_id=course_id,
            learner_id=learner_id,
            lessons=lessons,
            slides=slides,
        )

    async def get_lesson(self, course_id: str, lesson_id: str) -> LessonDetailResponse:
        lesson = self.corpus.lessons[lesson_id]
        return LessonDetailResponse(
            course_id=course_id,
            lesson_id=lesson.lesson_id,
            title=lesson.title,
            transcript_markdown=transcript_body(lesson.transcript_markdown),
            transcript_file=lesson.transcript_file,
            transcript_viewer_path=f"/api/assets/transcripts/{lesson.transcript_file}",
            slide_file=lesson.source_slide_file,
            slide_viewer_path=(
                f"/api/assets/slides/{lesson.source_slide_file}"
                if lesson.source_slide_file
                else None
            ),
        )
