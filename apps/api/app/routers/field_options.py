from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.field import FieldOptionCreate, FieldOptionRead, FieldOptionUpdate, ReorderRequest
from app.services import NotFoundError, ValidationAppError
from app.services.field_option import FieldOptionService

router = APIRouter(tags=["dynamic-fields"])


@router.post("/field-options", response_model=FieldOptionRead, status_code=status.HTTP_201_CREATED)
def create_option(payload: FieldOptionCreate, db: Session = Depends(get_db)) -> FieldOptionRead:
    try:
        option = FieldOptionService(db).create(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldOptionRead.model_validate(option)


@router.get("/field-definitions/{field_id}/options", response_model=list[FieldOptionRead])
def list_options(field_id: uuid.UUID, db: Session = Depends(get_db)) -> list[FieldOptionRead]:
    options = FieldOptionService(db).list_for_field(field_id)
    return [FieldOptionRead.model_validate(o) for o in options]


@router.patch("/field-options/{option_id}", response_model=FieldOptionRead)
def update_option(
    option_id: uuid.UUID, payload: FieldOptionUpdate, db: Session = Depends(get_db)
) -> FieldOptionRead:
    try:
        option = FieldOptionService(db).update(option_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldOptionRead.model_validate(option)


@router.post("/field-options/{option_id}/enable", response_model=FieldOptionRead)
def enable_option(option_id: uuid.UUID, db: Session = Depends(get_db)) -> FieldOptionRead:
    try:
        option = FieldOptionService(db).set_active(option_id, True)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldOptionRead.model_validate(option)


@router.post("/field-options/{option_id}/disable", response_model=FieldOptionRead)
def disable_option(option_id: uuid.UUID, db: Session = Depends(get_db)) -> FieldOptionRead:
    try:
        option = FieldOptionService(db).set_active(option_id, False)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FieldOptionRead.model_validate(option)


@router.post("/field-definitions/{field_id}/options/reorder", response_model=list[FieldOptionRead])
def reorder_options(
    field_id: uuid.UUID, payload: ReorderRequest, db: Session = Depends(get_db)
) -> list[FieldOptionRead]:
    try:
        options = FieldOptionService(db).reorder(field_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [FieldOptionRead.model_validate(o) for o in options]


@router.delete("/field-options/{option_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_option(option_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        FieldOptionService(db).delete(option_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
