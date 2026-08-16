from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.enums import TradeDirection, TradeStatus
from app.models.types import portable_enum


class Trade(UUIDPKMixin, TimestampMixin, Base):
    """جدول مرکزی معاملات. ستون‌های اصلی طبق پرامپت مادر عیناً پیاده‌سازی
    شده‌اند. فیلدهای اختصاصی/داینامیک کاربر در trade_field_values ذخیره
    می‌شوند و از این طریق درگیر تحلیل، فیلتر و بینش‌ها می‌شوند."""

    __tablename__ = "trades"
    __table_args__ = (
        UniqueConstraint("account_id", "import_hash", name="uq_trades_account_import_hash"),
        Index("ix_trades_account_entry_time", "account_id", "entry_time"),
        Index("ix_trades_symbol_id", "symbol_id"),
        Index("ix_trades_status", "status"),
        Index("ix_trades_needs_review", "needs_review"),
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    symbol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("symbols.id", ondelete="RESTRICT"), nullable=False
    )

    direction: Mapped[TradeDirection] = mapped_column(
        portable_enum(TradeDirection, "trade_direction"), nullable=False
    )
    status: Mapped[TradeStatus] = mapped_column(
        portable_enum(TradeStatus, "trade_status"), nullable=False, default=TradeStatus.OPEN
    )

    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)

    entry_price: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    exit_price: Mapped[Optional[float]] = mapped_column(Numeric(18, 6))
    stop_loss: Mapped[Optional[float]] = mapped_column(Numeric(18, 6))
    take_profit: Mapped[Optional[float]] = mapped_column(Numeric(18, 6))

    volume: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    commission: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    swap: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)

    gross_profit: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    net_profit: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    risk_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    risk_percent: Mapped[Optional[float]] = mapped_column(Numeric(9, 4))
    r_multiple: Mapped[Optional[float]] = mapped_column(Numeric(9, 4))
    pips: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))

    balance_before: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    balance_after: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))

    external_id: Mapped[Optional[str]] = mapped_column(String(200))
    broker_ticket: Mapped[Optional[str]] = mapped_column(String(100))
    position_id: Mapped[Optional[str]] = mapped_column(String(100))
    magic_number: Mapped[Optional[str]] = mapped_column(String(100))

    import_source: Mapped[Optional[str]] = mapped_column(String(50))
    import_hash: Mapped[Optional[str]] = mapped_column(String(128))
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    custom: Mapped[Optional[dict]] = mapped_column(JSONB)

    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    review_status: Mapped[Optional[str]] = mapped_column(String(30))

    # --- روابط ---------------------------------------------------------------
    account: Mapped["Account"] = relationship(back_populates="trades")
    symbol: Mapped["Symbol"] = relationship(back_populates="trades")
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="trade", cascade="all, delete-orphan"
    )
    field_values: Mapped[list["TradeFieldValue"]] = relationship(
        back_populates="trade", cascade="all, delete-orphan"
    )
    checklist_answers: Mapped[list["TradeChecklistAnswer"]] = relationship(
        back_populates="trade", cascade="all, delete-orphan"
    )
    mistake_costs: Mapped[list["MistakeCost"]] = relationship(
        back_populates="trade", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Trade {self.id} {self.direction} {self.status}>"
