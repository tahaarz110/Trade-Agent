from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.schemas.pagination import Page, PaginationParams
from app.services import NotFoundError, ValidationAppError
from app.services.account import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)) -> AccountRead:
    account = AccountService(db).create(payload)
    return AccountRead.model_validate(account)


@router.get("", response_model=Page[AccountRead])
def list_accounts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> Page[AccountRead]:
    pagination = PaginationParams(page=page, page_size=page_size)
    items, total = AccountService(db).list(pagination)
    return Page.create(
        items=[AccountRead.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{account_id}", response_model=AccountRead)
def get_account(account_id: uuid.UUID, db: Session = Depends(get_db)) -> AccountRead:
    try:
        account = AccountService(db).get(account_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AccountRead.model_validate(account)


@router.patch("/{account_id}", response_model=AccountRead)
def update_account(
    account_id: uuid.UUID, payload: AccountUpdate, db: Session = Depends(get_db)
) -> AccountRead:
    try:
        account = AccountService(db).update(account_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AccountRead.model_validate(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_account(account_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        AccountService(db).delete(account_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationAppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
