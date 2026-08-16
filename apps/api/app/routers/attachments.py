from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attachment import AttachmentRead
from app.services import NotFoundError, ValidationAppError
from app.services.attachment import AttachmentService

router = APIRouter(tags=["attachments"])


@router.post(
    "/trades/{trade_id}/attachments",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    trade_id: uuid.UUID,
    file: UploadFile = File(...),
    caption: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> AttachmentRead:
    """آپلود یک فایل/تصویر و اتصال آن به معامله. برای تصاویر، تصویر
    بندانگشتی به‌صورت خودکار ساخته می‌شود."""
    try:
        attachment = AttachmentService(db).upload(
            trade_id=trade_id,
            file_name=file.filename or "attachment",
            content_type=file.content_type,
            file_obj=file.file,
            caption=caption,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return AttachmentRead.model_validate(attachment)


@router.get("/trades/{trade_id}/attachments", response_model=list[AttachmentRead])
def list_attachments(trade_id: uuid.UUID, db: Session = Depends(get_db)) -> list[AttachmentRead]:
    try:
        items = AttachmentService(db).list_for_trade(trade_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [AttachmentRead.model_validate(i) for i in items]


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_attachment(attachment_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        AttachmentService(db).delete(attachment_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
