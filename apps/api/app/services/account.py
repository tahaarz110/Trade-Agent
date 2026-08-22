from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.account import Account
from app.repositories.account import AccountRepository
from app.schemas.account import AccountCreate, AccountUpdate
from app.schemas.pagination import PaginationParams
from app.services import NotFoundError, ValidationAppError


class AccountService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AccountRepository(db)

    def create(self, payload: AccountCreate) -> Account:
        account = Account(**payload.model_dump())
        self.repo.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def get(self, account_id: uuid.UUID) -> Account:
        account = self.repo.get(account_id)
        if not account:
            raise NotFoundError("حساب", account_id)
        return account

    def list(self, pagination: PaginationParams) -> tuple[list[Account], int]:
        return self.repo.list_paginated(
            offset=pagination.offset,
            limit=pagination.page_size,
            order_by=Account.created_at.desc(),
        )

    def update(self, account_id: uuid.UUID, payload: AccountUpdate) -> Account:
        account = self.get(account_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(account, key, value)
        self.db.commit()
        self.db.refresh(account)
        return account

    def delete(self, account_id: uuid.UUID) -> None:
        account = self.get(account_id)
        try:
            self.repo.delete(account)
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValidationAppError(
                "این حساب دارای معاملات یا سابقه ایمپورت ثبت‌شده است و برای حفظ یکپارچگی تاریخچه "
                "قابل حذف نیست؛ به‌جای حذف، آن را غیرفعال کنید"
            ) from exc
