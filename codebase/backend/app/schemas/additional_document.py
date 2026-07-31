from pydantic import BaseModel


class AdditionalDocument(BaseModel):
    document_id: str
    title: str
    file_name: str
    viewer_path: str
    created_at: str


class StagedAdditionalDocument(BaseModel):
    stage_id: str
    file_name: str
    viewer_path: str
