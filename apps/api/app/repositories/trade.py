from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import Select

from app.models.enums import TradeDirection, TradeStatus
from app.models.trade import Trade
from app.repositories.base import BaseRepository


@dataclass
class TradeFilters:
    account_id: Optional[uuid.UUID] = None
    symbol_id: Optional[uuid.UUID] = None
    direction: Optional[TradeDirection] = None
    status: Optional[TradeStatus] = None
    review_status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    field_id: Optional[uuid.UUID] = None
    field_value: Optional[str] = None

    def apply(self, stmt: Select) -> Select:
        if self.account_id is not None:
            stmt = stmt.where(Trade.account_id == self.account_id)
        if self.symbol_id is not None:
            stmt = stmt.where(Trade.symbol_id == self.symbol_id)
        if self.direction is not None:
            stmt = stmt.where(Trade.direction == self.direction)
        if self.status is not None:
            stmt = stmt.where(Trade.status == self.status)
        if self.review_status is not None:
            stmt = stmt.where(Trade.review_status == self.review_status)
        if self.date_from is not None:
            stmt = stmt.where(
                Trade.entry_time
                >= datetime.combine(self.date_from, datetime.min.time(), tzinfo=timezone.utc)
            )
        if self.date_to is not None:
            stmt = stmt.where(
                Trade.entry_time
                <= datetime.combine(self.date_to, datetime.max.time(), tzinfo=timezone.utc)
            )
        return stmt


class TradeRepository(BaseRepository[Trade]):
    model = Trade

    def list_filtered(
        self, *, filters: TradeFilters, offset: int, limit: int
    ) -> tuple[Sequence[Trade], int]:
        from app.models.field import TradeFieldValue

        def _filter_fn(stmt: Select) -> Select:
            stmt = filters.apply(stmt)
            if filters.field_id is not None:
                stmt = stmt.join(
                    TradeFieldValue,
                    (TradeFieldValue.trade_id == Trade.id)
                    & (TradeFieldValue.field_id == filters.field_id),
                )
                if filters.field_value is not None:
                    stmt = stmt.where(
                        (TradeFieldValue.value_text == filters.field_value)
                        | (TradeFieldValue.value_json.contains([filters.field_value]))
                    )
            return stmt

        return self.list_paginated(
            offset=offset,
            limit=limit,
            filter_fn=_filter_fn,
            order_by=Trade.entry_time.desc(),
        )
