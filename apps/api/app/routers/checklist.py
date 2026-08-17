from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.checklist import (
    ChecklistItemCreate,
    ChecklistItemRead,
    ChecklistItemUpdate,
    ChecklistTemplateCreate,
    ChecklistTemplateRead,
    ChecklistTemplateUpdate,
)
from app.schemas.common import ReorderRequest
from app.services import NotFoundError, ValidationAppError
from app.services.checklist import ChecklistItemService, ChecklistTemplateService

router = APIRouter(prefix="/checklist-templates", tags=["checklist"])


@router.post("", response_model=ChecklistTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: ChecklistTemplateCreate, db: Session = Depends(get_db)
) -> ChecklistTemplateRead:
    template = ChecklistTemplateService(db).create(payload)
    return ChecklistTemplateRead.model_validate(template)


@router.get("", response_model=list[ChecklistTemplateRead])
def list_templates(
    include_inactive: bool = Query(default=True), db: Session = Depends(get_db)
) -> list[ChecklistTemplateRead]:
    templates = ChecklistTemplateService(db).list(include_inactive=include_inactive)
    return [ChecklistTemplateRead.model_validate(t) for t in templates]


@router.get("/{template_id}", response_model=ChecklistTemplateRead)
def get_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> ChecklistTemplateRead:
    try:
        template = ChecklistTemplateService(db).get(template_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChecklistTemplateRead.model_validate(template)


@router.patch("/{template_id}", response_model=ChecklistTemplateRead)
def update_template(
    template_id: uuid.UUID, payload: ChecklistTemplateUpdate, db: Session = Depends(get_db)
) -> ChecklistTemplateRead:
    try:
        template = ChecklistTemplateService(db).update(template_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChecklistTemplateRead.model_validate(template)


@router.post("/{template_id}/enable", response_model=ChecklistTemplateRead)
def enable_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> ChecklistTemplateRead:
    try:
        template = ChecklistTemplateService(db).set_active(template_id, True)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChecklistTemplateRead.model_validate(template)


@router.post("/{template_id}/disable", response_model=ChecklistTemplateRead)
def disable_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> ChecklistTemplateRead:
    try:
        template = ChecklistTemplateService(db).set_active(template_id, False)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChecklistTemplateRead.model_validate(template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        ChecklistTemplateService(db).delete(template_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# --- آیتم‌های چک‌لیست ---------------------------------------------------------------
@router.post("/items", response_model=ChecklistItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ChecklistItemCreate, db: Session = Depends(get_db)) -> ChecklistItemRead:
    try:
        item = ChecklistItemService(db).create(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChecklistItemRead.model_validate(item)


@router.get("/{template_id}/items", response_model=list[ChecklistItemRead])
def list_items(template_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ChecklistItemRead]:
    items = ChecklistItemService(db).list_for_template(template_id)
    return [ChecklistItemRead.model_validate(i) for i in items]


@router.patch("/items/{item_id}", response_model=ChecklistItemRead)
def update_item(
    item_id: uuid.UUID, payload: ChecklistItemUpdate, db: Session = Depends(get_db)
) -> ChecklistItemRead:
    try:
        item = ChecklistItemService(db).update(item_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChecklistItemRead.model_validate(item)


@router.post("/{template_id}/items/reorder", response_model=list[ChecklistItemRead])
def reorder_items(
    template_id: uuid.UUID, payload: ReorderRequest, db: Session = Depends(get_db)
) -> list[ChecklistItemRead]:
    try:
        items = ChecklistItemService(db).reorder(template_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [ChecklistItemRead.model_validate(i) for i in items]


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_item(item_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        ChecklistItemService(db).delete(item_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
