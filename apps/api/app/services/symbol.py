from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.symbol import Symbol
from app.repositories.symbol import SymbolRepository
from app.schemas.pagination import PaginationParams
from app.schemas.symbol import SymbolCreate, SymbolUpdate
from app.services import ConflictError, NotFoundError


class SymbolService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SymbolRepository(db)

    def create(self, payload: SymbolCreate) -> Symbol:
        symbol = Symbol(**payload.model_dump())
        try:
            self.repo.add(symbol)
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(f"نمادی با نام «{payload.name}» از قبل وجود دارد") from exc
        self.db.refresh(symbol)
        return symbol

    def get(self, symbol_id: uuid.UUID) -> Symbol:
        symbol = self.repo.get(symbol_id)
        if not symbol:
            raise NotFoundError("نماد", symbol_id)
        return symbol

    def list(self, pagination: PaginationParams) -> tuple[list[Symbol], int]:
        return self.repo.list_paginated(
            offset=pagination.offset,
            limit=pagination.page_size,
            order_by=Symbol.name.asc(),
        )

    def update(self, symbol_id: uuid.UUID, payload: SymbolUpdate) -> Symbol:
        symbol = self.get(symbol_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(symbol, key, value)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("این تغییر با نماد دیگری تعارض دارد") from exc
        self.db.refresh(symbol)
        return symbol

    def delete(self, symbol_id: uuid.UUID) -> None:
        symbol = self.get(symbol_id)
        self.repo.delete(symbol)
        self.db.commit()
