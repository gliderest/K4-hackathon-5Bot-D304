from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.app.core.runtime import runtime
from backend.app.schemas.upload import UploadResponse


router = APIRouter()


@router.post("", response_model=UploadResponse)
async def upload_document(
    learner_id: str = Form(...),
    file: UploadFile = File(...),
) -> UploadResponse:
    try:
        return await runtime.upload_service.save_upload(learner_id=learner_id, file=file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
