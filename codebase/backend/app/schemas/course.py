from pydantic import BaseModel, Field


class CourseLesson(BaseModel):
    lesson_id: str
    title: str
    transcript_file: str
    slide_file: str | None = None
    slide_viewer_path: str | None = None
    segment_count: int = 0
    completion_percent: int = 0


class CourseSlide(BaseModel):
    slide_id: str
    title: str
    slide_file: str
    slide_viewer_path: str


class CourseOutlineResponse(BaseModel):
    course_id: str
    learner_id: str
    lessons: list[CourseLesson] = Field(default_factory=list)
    slides: list[CourseSlide] = Field(default_factory=list)


class LessonDetailResponse(BaseModel):
    course_id: str
    lesson_id: str
    title: str
    transcript_markdown: str
    transcript_viewer_path: str
    slide_file: str | None = None
    slide_viewer_path: str | None = None
