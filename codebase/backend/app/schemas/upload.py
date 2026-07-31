from pydantic import BaseModel


class UploadResponse(BaseModel):
    learner_id: str
    conversation_id: str
    document_id: str
    file_name: str
    viewer_path: str
    chunk_count: int
