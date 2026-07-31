import json
import re
from pathlib import Path

import fitz

from backend.app.core.config import Settings
from backend.app.rag.contracts import LessonRecord, SourceChunk
from backend.app.rag.embeddings import OpenAIEmbeddingService, vector_store_path


TOKEN_PATTERN = re.compile(r"[0-9A-Za-zA-ZÀ-ỹ]+", re.UNICODE)
TRANSCRIPT_SEGMENT_PATTERN = re.compile(r"\*\*\[(?P<segment>[^\]]+)\]\*\*\s*(?P<text>.+)")
TRANSCRIPT_TITLE_PATTERN = re.compile(r"^##\s+(?P<title>.+)$")


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


def lesson_number_from_name(name: str) -> int:
    match = re.search(r"(\d+)", name)
    return int(match.group(1)) if match else 0


class CourseCorpus:
    def __init__(
        self,
        settings: Settings,
        embedding_service: OpenAIEmbeddingService | None = None,
    ) -> None:
        self.settings = settings
        self.embedding_service = embedding_service
        self.course_chunks: list[SourceChunk] = []
        self.lessons: dict[str, LessonRecord] = {}
        self.chunk_vectors: dict[str, list[float]] = {}

    async def build(self) -> None:
        self.course_chunks = []
        self.lessons = {}
        transcript_dir = self.settings.resolve_path(self.settings.transcripts_dir)
        slide_dir = self.settings.resolve_path(self.settings.slides_dir)
        transcript_files = sorted(transcript_dir.glob("*.md"))
        slide_files = sorted(slide_dir.glob("*.pdf"))

        for transcript_file in transcript_files:
            lesson_id, lesson_title, segment_ids, transcript_markdown = self._parse_transcript(
                transcript_file
            )
            slide_file = self._map_slide_to_lesson(lesson_id, slide_files)
            self.lessons[lesson_id] = LessonRecord(
                lesson_id=lesson_id,
                title=lesson_title,
                transcript_file=transcript_file.name,
                transcript_markdown=transcript_markdown,
                source_slide_file=slide_file.name if slide_file else None,
                source_slide_label=slide_file.stem if slide_file else None,
                segment_ids=segment_ids,
            )

        for lesson in self.lessons.values():
            self.course_chunks.extend(
                self._build_transcript_chunks(
                    lesson_id=lesson.lesson_id,
                    title=lesson.title,
                    transcript_file=transcript_dir / lesson.transcript_file,
                )
            )

        for slide_file in slide_files:
            self.course_chunks.extend(self._build_slide_chunks(slide_file))

        self._write_catalog_snapshot()
        await self._load_or_create_embeddings()

    def _map_slide_to_lesson(self, lesson_id: str, slide_files: list[Path]) -> Path | None:
        if not slide_files:
            return None
        if len(slide_files) == 1:
            return slide_files[0]
        lesson_number = lesson_number_from_name(lesson_id)
        if lesson_number <= 3:
            return slide_files[0]
        return slide_files[-1]

    def _parse_transcript(self, transcript_file: Path) -> tuple[str, str, list[str], str]:
        text = transcript_file.read_text(encoding="utf-8")
        lesson_number = lesson_number_from_name(transcript_file.stem)
        lesson_id = f"lesson-{lesson_number:02d}"
        title = f"Lesson {lesson_number:02d}"
        segment_ids: list[str] = []
        for line in text.splitlines():
            title_match = TRANSCRIPT_TITLE_PATTERN.match(line.strip())
            if title_match and title == f"Lesson {lesson_number:02d}":
                title = title_match.group("title").strip()
            segment_match = TRANSCRIPT_SEGMENT_PATTERN.search(line)
            if segment_match:
                segment_ids.append(segment_match.group("segment").strip())
        return lesson_id, title, segment_ids, text

    def _build_transcript_chunks(
        self,
        lesson_id: str,
        title: str,
        transcript_file: Path,
    ) -> list[SourceChunk]:
        chunks: list[SourceChunk] = []
        for line in transcript_file.read_text(encoding="utf-8").splitlines():
            segment_match = TRANSCRIPT_SEGMENT_PATTERN.search(line)
            if not segment_match:
                continue
            segment_id = segment_match.group("segment").strip()
            text = segment_match.group("text").strip()
            chunks.append(
                SourceChunk(
                    chunk_id=f"{lesson_id}:{segment_id}",
                    text=text,
                    course_id=self.settings.course_id,
                    lesson_id=lesson_id,
                    title=title,
                    source_type="transcript",
                    source_file=transcript_file.name,
                    segment_id=segment_id,
                    metadata={"tokens": " ".join(sorted(tokenize(text)))},
                )
            )
        return chunks

    def _build_slide_chunks(self, slide_file: Path) -> list[SourceChunk]:
        chunks: list[SourceChunk] = []
        with fitz.open(slide_file) as document:
            for page_index, page in enumerate(document, start=1):
                page_text = " ".join(page.get_text("text").split())
                if len(page_text) < 20:
                    continue
                lesson_number = 1 if "d1" in slide_file.stem.lower() else 4
                lesson_id = f"lesson-{lesson_number:02d}"
                chunks.append(
                    SourceChunk(
                        chunk_id=f"{slide_file.stem}:page-{page_index}",
                        text=page_text,
                        course_id=self.settings.course_id,
                        lesson_id=lesson_id,
                        title=slide_file.stem,
                        source_type="slide",
                        source_file=slide_file.name,
                        page=page_index,
                        metadata={"tokens": " ".join(sorted(tokenize(page_text)))},
                    )
                )
        return chunks

    def _write_catalog_snapshot(self) -> None:
        target_dir = self.settings.resolve_path(self.settings.chunks_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        catalog_path = target_dir / "catalog.json"
        payload = {
            "course_id": self.settings.course_id,
            "lessons": [
                {
                    "lesson_id": lesson.lesson_id,
                    "title": lesson.title,
                    "transcript_file": lesson.transcript_file,
                    "source_slide_file": lesson.source_slide_file,
                    "segment_count": len(lesson.segment_ids),
                }
                for lesson in self.lessons.values()
            ],
        }
        catalog_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    async def _load_or_create_embeddings(self) -> None:
        if not self.embedding_service or not self.embedding_service.enabled:
            self.chunk_vectors = {}
            return

        store_path = vector_store_path(
            self.settings.resolve_path(self.settings.vector_store_dir),
            "course_embeddings.json",
        )
        if store_path.exists():
            payload = json.loads(store_path.read_text(encoding="utf-8"))
            if payload.get("model") == self.settings.embedding_model:
                self.chunk_vectors = {
                    item["chunk_id"]: item["embedding"] for item in payload.get("items", [])
                }
                missing_ids = [
                    chunk.chunk_id for chunk in self.course_chunks if chunk.chunk_id not in self.chunk_vectors
                ]
                if not missing_ids:
                    return

        texts = [chunk.text for chunk in self.course_chunks]
        vectors = await self.embedding_service.embed_texts(texts)
        self.chunk_vectors = {
            chunk.chunk_id: vector for chunk, vector in zip(self.course_chunks, vectors, strict=False)
        }
        payload = {
            "model": self.settings.embedding_model,
            "items": [
                {"chunk_id": chunk.chunk_id, "embedding": self.chunk_vectors.get(chunk.chunk_id, [])}
                for chunk in self.course_chunks
            ],
        }
        store_path.write_text(json.dumps(payload), encoding="utf-8")
