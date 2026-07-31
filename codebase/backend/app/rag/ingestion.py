import hashlib
import json
import re
from pathlib import Path

import fitz

from backend.app.core.config import Settings
from backend.app.rag.contracts import LessonRecord, SourceChunk
from backend.app.rag.embeddings import OpenAIEmbeddingService, vector_store_path


TOKEN_PATTERN = re.compile(r"[0-9A-Za-zA-ZÀ-ỹ]+", re.UNICODE)
TRANSCRIPT_SEGMENT_PATTERN = re.compile(r"\*\*\[(?P<segment>[^\]]+)\]\*\*\s*(?P<text>.+)")
TRANSCRIPT_TITLE_PATTERN = re.compile(r"^#{1,6}\s+(?P<title>.+)$")
TRANSCRIPT_PREFIX_PATTERN = re.compile(r"^Transcript bài giảng\s*(?:\([^)]*\))?\s*[—-]\s*", re.IGNORECASE)


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
        self.slide_documents: list[dict[str, str]] = []
        self.chunk_vectors: dict[str, list[float]] = {}

    async def build(self) -> None:
        self.course_chunks = []
        self.lessons = {}
        self.slide_documents = []
        transcript_dir = self.settings.resolve_path(self.settings.transcripts_dir)
        slide_dir = self.settings.resolve_path(self.settings.slides_dir)
        # README describes the data pack; it is not a lesson transcript.
        transcript_files = sorted(
            file for file in transcript_dir.glob("*.md") if file.name.lower() != "readme.md"
        )
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
            self.slide_documents.append({
                "slide_id": slide_file.stem,
                "slide_file": slide_file.name,
                "title": self._extract_slide_title(slide_file),
            })
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
                title = TRANSCRIPT_PREFIX_PATTERN.sub("", title_match.group("title").strip())
            segment_match = TRANSCRIPT_SEGMENT_PATTERN.search(line)
            if segment_match:
                segment_ids.append(segment_match.group("segment").strip())
        return lesson_id, title, segment_ids, text

    def _extract_slide_title(self, slide_file: Path) -> str:
        """Use the largest text on page one as the slide deck title."""
        try:
            with fitz.open(slide_file) as document:
                if not document.page_count:
                    return slide_file.stem
                candidates: list[tuple[float, str]] = []
                for block in document[0].get_text("dict").get("blocks", []):
                    for line in block.get("lines", []):
                        text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
                        if text:
                            size = max((span.get("size", 0.0) for span in line.get("spans", [])), default=0.0)
                            candidates.append((size, text))
                if candidates:
                    return max(candidates, key=lambda candidate: candidate[0])[1]
        except (fitz.FileDataError, RuntimeError, ValueError):
            pass
        return slide_file.stem

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
        """Create page and text-block chunks with slide-specific semantic context."""
        chunks: list[SourceChunk] = []
        deck_title = self._extract_slide_title(slide_file)
        lesson_number = 1 if "d1" in slide_file.stem.lower() else 4
        lesson_id = f"lesson-{lesson_number:02d}"

        with fitz.open(slide_file) as document:
            for page_index, page in enumerate(document, start=1):
                text_blocks = self._extract_page_text_blocks(page)
                if not text_blocks:
                    continue

                page_title = self._extract_page_title(text_blocks, fallback=deck_title)
                page_content = "\n".join(block["text"] for block in text_blocks)
                page_text = self._slide_context(
                    deck_title=deck_title,
                    page_title=page_title,
                    page_index=page_index,
                    content=page_content,
                )
                chunks.append(
                    self._make_slide_chunk(
                        chunk_id=f"{slide_file.stem}:page-{page_index}:overview",
                        text=page_text,
                        lesson_id=lesson_id,
                        title=page_title,
                        slide_file=slide_file,
                        page_index=page_index,
                    )
                )

                # A deck page often contains several unrelated concepts. Indexing each
                # visible block separately makes semantic search precise enough to cite
                # the actual slide rather than a similar transcript sentence.
                for block_index, block in enumerate(text_blocks, start=1):
                    if len(block["text"]) < 24:
                        continue
                    block_text = self._slide_context(
                        deck_title=deck_title,
                        page_title=page_title,
                        page_index=page_index,
                        content=block["text"],
                    )
                    chunks.append(
                        self._make_slide_chunk(
                            chunk_id=f"{slide_file.stem}:page-{page_index}:block-{block_index}",
                            text=block_text,
                            lesson_id=lesson_id,
                            title=page_title,
                            slide_file=slide_file,
                            page_index=page_index,
                        )
                    )
        return chunks

    @staticmethod
    def _extract_page_text_blocks(page: fitz.Page) -> list[dict[str, float | str]]:
        """Read PDF text in visual order and retain font size for title detection."""
        blocks: list[dict[str, float | str]] = []
        seen_text: set[str] = set()
        for block in page.get_text("dict").get("blocks", []):
            if block.get("type") != 0:
                continue
            lines = block.get("lines", [])
            parts = []
            font_sizes = []
            for line in lines:
                line_text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
                if line_text:
                    parts.append(line_text)
                    font_sizes.extend(span.get("size", 0.0) for span in line.get("spans", []))
            text = " ".join(parts).strip()
            normalized = re.sub(r"\s+", " ", text)
            if len(normalized) < 3 or normalized in seen_text or re.fullmatch(r"\d+", normalized):
                continue
            seen_text.add(normalized)
            bbox = block.get("bbox", (0.0, 0.0, 0.0, 0.0))
            blocks.append(
                {
                    "text": normalized,
                    "font_size": max(font_sizes, default=0.0),
                    "y": bbox[1],
                    "x": bbox[0],
                }
            )
        return sorted(blocks, key=lambda item: (float(item["y"]), float(item["x"])))

    @staticmethod
    def _extract_page_title(blocks: list[dict[str, float | str]], fallback: str) -> str:
        title_candidates = [
            block for block in blocks if 3 <= len(str(block["text"])) <= 180
        ]
        if not title_candidates:
            return fallback
        return str(
            max(
                title_candidates,
                key=lambda block: (float(block["font_size"]), -float(block["y"])),
            )["text"]
        )

    @staticmethod
    def _slide_context(deck_title: str, page_title: str, page_index: int, content: str) -> str:
        return (
            f"Bộ slide: {deck_title}\n"
            f"Trang {page_index} — {page_title}\n"
            f"Nội dung slide: {content}"
        )

    def _make_slide_chunk(
        self,
        chunk_id: str,
        text: str,
        lesson_id: str,
        title: str,
        slide_file: Path,
        page_index: int,
    ) -> SourceChunk:
        return SourceChunk(
            chunk_id=chunk_id,
            text=text,
            course_id=self.settings.course_id,
            lesson_id=lesson_id,
            title=title,
            source_type="slide",
            source_file=slide_file.name,
            page=page_index,
            metadata={"tokens": " ".join(sorted(tokenize(text)))},
        )

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
            "slides": self.slide_documents,
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
        corpus_fingerprint = self._corpus_fingerprint()
        if store_path.exists():
            payload = json.loads(store_path.read_text(encoding="utf-8"))
            if (
                payload.get("model") == self.settings.embedding_model
                and payload.get("corpus_fingerprint") == corpus_fingerprint
            ):
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
            "corpus_fingerprint": corpus_fingerprint,
            "items": [
                {"chunk_id": chunk.chunk_id, "embedding": self.chunk_vectors.get(chunk.chunk_id, [])}
                for chunk in self.course_chunks
            ],
        }
        store_path.write_text(json.dumps(payload), encoding="utf-8")

    def _corpus_fingerprint(self) -> str:
        content = "\n".join(
            f"{chunk.chunk_id}\0{chunk.source_type}\0{chunk.text}" for chunk in self.course_chunks
        )
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
