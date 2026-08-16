from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import TradeDirection, TradeStatus
from app.repositories.trade import TradeFilters
from app.schemas.pagination import Page, PaginationParams
from app.schemas.trade import TradeCreate, TradeDetailRead, TradeRead, TradeUpdate
from app.services import ConflictError, NotFoundError, ValidationAppError
from app.services.trade import TradeService

router = APIRouter(prefix="/trades", tags=["trades"])


@router.post("", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
def create_trade(payload: TradeCreate, db: Session = Depends(get_db)) -> TradeRead:
    try:
        trade = TradeService(db).create(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return TradeRead.model_validate(trade)


@router.get("", response_model=Page[TradeRead])
def list_trades(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    account_id: Optional[uuid.UUID] = None,
    symbol_id: Optional[uuid.UUID] = None,
    direction: Optional[TradeDirection] = None,
    status_: Optional[TradeStatus] = Query(default=None, alias="status"),
    review_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    field_id: Optional[uuid.UUID] = None,
    field_value: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Page[TradeRead]:
    """فهرست صفحه‌بندی‌شده معاملات با فیلتر بر اساس حساب، نماد، جهت،
    وضعیت، وضعیت بازبینی، بازه تاریخ، و فیلد پویا (field_id + field_value)."""
    pagination = PaginationParams(page=page, page_size=page_size)
    filters = TradeFilters(
        account_id=account_id,
        symbol_id=symbol_id,
        direction=direction,
        status=status_,
        review_status=review_status,
        date_from=date_from,
        date_to=date_to,
        field_id=field_id,
        field_value=field_value,
    )
    items, total = TradeService(db).list(
        filters=filters, offset=pagination.offset, limit=pagination.page_size
    )
    return Page.create(
        items=[TradeRead.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{trade_id}", response_model=TradeDetailRead)
def get_trade(trade_id: uuid.UUID, db: Session = Depends(get_db)) -> TradeDetailRead:
    """جزئیات یک معامله شامل ستون‌های اصلی و مقادیر فیلدهای پویا."""
    try:
        return TradeService(db).get_detail(trade_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{trade_id}", response_model=TradeRead)
def update_trade(
    trade_id: uuid.UUID, payload: TradeUpdate, db: Session = Depends(get_db)
) -> TradeRead:
    try:
        trade = TradeService(db).update(trade_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return TradeRead.model_validate(trade)


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_trade(trade_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        TradeService(db).delete(trade_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
