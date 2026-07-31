from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.core.runtime import runtime
from backend.app.schemas.additional_document import AdditionalDocument, StagedAdditionalDocument


router = APIRouter()


@router.get("", response_model=list[AdditionalDocument])
async def list_documents() -> list[AdditionalDocument]:
    return await runtime.additional_document_store.list()


@router.post("/stage", response_model=StagedAdditionalDocument)
async def stage_document(file: UploadFile = File(...)) -> StagedAdditionalDocument:
    try:
        return await runtime.additional_document_service.stage(file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/{stage_id}/confirm", response_model=AdditionalDocument)
async def confirm_document(stage_id: str) -> AdditionalDocument:
    try:
        return await runtime.additional_document_service.confirm(stage_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/{stage_id}", status_code=204)
async def cancel_document(stage_id: str) -> None:
    await runtime.additional_document_service.cancel(stage_id)
