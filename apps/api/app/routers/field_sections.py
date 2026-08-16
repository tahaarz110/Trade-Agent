from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.field import (
    FieldSectionCreate,
    FieldSectionRead,
    FieldSectionUpdate,
    ReorderRequest,
)
from app.services import ConflictError, NotFoundError, ValidationAppError
from app.services.field_section import FieldSectionService

router = APIRouter(prefix="/field-sections", tags=["dynamic-fields"])


@router.post("", response_model=FieldSectionRead, status_code=status.HTTP_201_CREATED)
def create_section(payload: FieldSectionCreate, db: Session = Depends(get_db)) -> FieldSectionRead:
    try:
        section = FieldSectionService(db).create(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return FieldSectionRead.model_validate(section)


@router.get("", response_model=list[FieldSectionRead])
def list_sections(
    include_inactive: bool = Query(default=True), db: Session = Depends(get_db)
) -> list[FieldSectionRead]:
    sections = FieldSectionService(db).list(include_inactive=include_inactive)
    return [FieldSectionRead.model_validate(s) for s in sections]


@router.get("/{section_id}", response_model=FieldSectionRead)
def get_section(section_id: uuid.UUID, db: Session = Depends(get_db)) -> FieldSectionRead:
    try:
        section = FieldSectionService(db).get(section_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldSectionRead.model_validate(section)


@router.patch("/{section_id}", response_model=FieldSectionRead)
def update_section(
    section_id: uuid.UUID, payload: FieldSectionUpdate, db: Session = Depends(get_db)
) -> FieldSectionRead:
    try:
        section = FieldSectionService(db).update(section_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldSectionRead.model_validate(section)


@router.post("/{section_id}/enable", response_model=FieldSectionRead)
def enable_section(section_id: uuid.UUID, db: Session = Depends(get_db)) -> FieldSectionRead:
    try:
        section = FieldSectionService(db).set_active(section_id, True)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldSectionRead.model_validate(section)


@router.post("/{section_id}/disable", response_model=FieldSectionRead)
def disable_section(section_id: uuid.UUID, db: Session = Depends(get_db)) -> FieldSectionRead:
    try:
        section = FieldSectionService(db).set_active(section_id, False)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldSectionRead.model_validate(section)


@router.post("/reorder", response_model=list[FieldSectionRead])
def reorder_sections(payload: ReorderRequest, db: Session = Depends(get_db)) -> list[FieldSectionRead]:
    try:
        sections = FieldSectionService(db).reorder(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [FieldSectionRead.model_validate(s) for s in sections]


@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_section(section_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        FieldSectionService(db).delete(section_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
