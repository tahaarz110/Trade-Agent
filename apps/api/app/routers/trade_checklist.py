from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.trade_checklist import TradeChecklistRead, TradeChecklistUpdate
from app.services import NotFoundError, ValidationAppError
from app.services.trade_checklist import TradeChecklistService

router = APIRouter(prefix="/trades", tags=["trade-checklist"])


@router.get("/{trade_id}/checklist", response_model=TradeChecklistRead)
def get_trade_checklist(trade_id: uuid.UUID, db: Session = Depends(get_db)) -> TradeChecklistRead:
    try:
        return TradeChecklistService(db).get(trade_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{trade_id}/checklist", response_model=TradeChecklistRead)
def update_trade_checklist(
    trade_id: uuid.UUID, payload: TradeChecklistUpdate, db: Session = Depends(get_db)
) -> TradeChecklistRead:
    try:
        return TradeChecklistService(db).update(trade_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/{trade_id}/checklist/assign-default",
    response_model=TradeChecklistRead,
    status_code=status.HTTP_200_OK,
)
def assign_default_checklist(trade_id: uuid.UUID, db: Session = Depends(get_db)) -> TradeChecklistRead:
    try:
        return TradeChecklistService(db).assign_default(trade_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
