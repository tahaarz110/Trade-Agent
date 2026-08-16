from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pagination import Page, PaginationParams
from app.schemas.symbol import SymbolCreate, SymbolRead, SymbolUpdate
from app.services import ConflictError, NotFoundError
from app.services.symbol import SymbolService

router = APIRouter(prefix="/symbols", tags=["symbols"])


@router.post("", response_model=SymbolRead, status_code=status.HTTP_201_CREATED)
def create_symbol(payload: SymbolCreate, db: Session = Depends(get_db)) -> SymbolRead:
    try:
        symbol = SymbolService(db).create(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return SymbolRead.model_validate(symbol)


@router.get("", response_model=Page[SymbolRead])
def list_symbols(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> Page[SymbolRead]:
    pagination = PaginationParams(page=page, page_size=page_size)
    items, total = SymbolService(db).list(pagination)
    return Page.create(
        items=[SymbolRead.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{symbol_id}", response_model=SymbolRead)
def get_symbol(symbol_id: uuid.UUID, db: Session = Depends(get_db)) -> SymbolRead:
    try:
        symbol = SymbolService(db).get(symbol_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SymbolRead.model_validate(symbol)


@router.patch("/{symbol_id}", response_model=SymbolRead)
def update_symbol(
    symbol_id: uuid.UUID, payload: SymbolUpdate, db: Session = Depends(get_db)
) -> SymbolRead:
    try:
        symbol = SymbolService(db).update(symbol_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return SymbolRead.model_validate(symbol)


@router.delete("/{symbol_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_symbol(symbol_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        SymbolService(db).delete(symbol_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
