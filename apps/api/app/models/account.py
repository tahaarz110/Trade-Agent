from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.enums import AccountType
from app.models.types import portable_enum


class Account(UUIDPKMixin, TimestampMixin, Base):
    """حساب معاملاتی (دمو/واقعی/پراپ). طبق پرامپت مادر: پشتیبانی از چند
    حساب همزمان از هر نوع."""

    __tablename__ = "accounts"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(
        portable_enum(AccountType, "account_type"), nullable=False
    )
    broker: Mapped[Optional[str]] = mapped_column(String(200))
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    initial_balance: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    current_balance: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    leverage: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    trades: Mapped[list["Trade"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    prop_rules: Mapped[list["PropRule"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Account {self.name} ({self.account_type})>"
