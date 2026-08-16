"""Repository پایه: کپسوله‌سازی دسترسی به دیتابیس، بدون منطق کسب‌وکار.

لایه Service از این کلاس‌ها استفاده می‌کند و قوانین کسب‌وکار (اعتبارسنجی،
محاسبات، تولید تصویر بندانگشتی و...) در آنجا پیاده‌سازی می‌شود.
"""
import uuid
from typing import Callable, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")

FilterFn = Callable[[Select], Select]


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, db: Session):
        self.db = db

    def get(self, id: uuid.UUID) -> Optional[ModelType]:
        return self.db.get(self.model, id)

    def list_paginated(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        filter_fn: Optional[FilterFn] = None,
        order_by=None,
    ) -> tuple[Sequence[ModelType], int]:
        stmt: Select = select(self.model)
        if filter_fn is not None:
            stmt = filter_fn(stmt)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        items = self.db.execute(stmt).scalars().all()
        return items, total

    def add(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.flush()
