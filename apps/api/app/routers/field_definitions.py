from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.field import (
    FieldDefinitionCreate,
    FieldDefinitionRead,
    FieldDefinitionUpdate,
    ReorderRequest,
)
from app.services import ConflictError, NotFoundError, ValidationAppError
from app.services.field_definition import FieldDefinitionService

router = APIRouter(prefix="/field-definitions", tags=["dynamic-fields"])


@router.post("", response_model=FieldDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_field(
    payload: FieldDefinitionCreate, db: Session = Depends(get_db)
) -> FieldDefinitionRead:
    try:
        field = FieldDefinitionService(db).create(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return FieldDefinitionRead.model_validate(field)


@router.get("", response_model=list[FieldDefinitionRead])
def list_fields(
    section_id: Optional[uuid.UUID] = None,
    include_inactive: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> list[FieldDefinitionRead]:
    fields = FieldDefinitionService(db).list(section_id=section_id, include_inactive=include_inactive)
    return [FieldDefinitionRead.model_validate(f) for f in fields]


@router.get("/{field_id}", response_model=FieldDefinitionRead)
def get_field(field_id: uuid.UUID, db: Session = Depends(get_db)) -> FieldDefinitionRead:
    try:
        field = FieldDefinitionService(db).get(field_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldDefinitionRead.model_validate(field)


@router.patch("/{field_id}", response_model=FieldDefinitionRead)
def update_field(
    field_id: uuid.UUID, payload: FieldDefinitionUpdate, db: Session = Depends(get_db)
) -> FieldDefinitionRead:
    try:
        field = FieldDefinitionService(db).update(field_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldDefinitionRead.model_validate(field)


@router.post("/{field_id}/enable", response_model=FieldDefinitionRead)
def enable_field(field_id: uuid.UUID, db: Session = Depends(get_db)) -> FieldDefinitionRead:
    try:
        field = FieldDefinitionService(db).set_active(field_id, True)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldDefinitionRead.model_validate(field)


@router.post("/{field_id}/disable", response_model=FieldDefinitionRead)
def disable_field(field_id: uuid.UUID, db: Session = Depends(get_db)) -> FieldDefinitionRead:
    try:
        field = FieldDefinitionService(db).set_active(field_id, False)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldDefinitionRead.model_validate(field)


@router.post("/reorder", response_model=list[FieldDefinitionRead])
def reorder_fields(
    payload: ReorderRequest, db: Session = Depends(get_db)
) -> list[FieldDefinitionRead]:
    try:
        fields = FieldDefinitionService(db).reorder(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [FieldDefinitionRead.model_validate(f) for f in fields]


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_field(field_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        FieldDefinitionService(db).delete(field_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
