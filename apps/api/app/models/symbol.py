from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class Symbol(UUIDPKMixin, TimestampMixin, Base):
    """نماد معاملاتی (مثلاً EURUSD). نام نماد یک فیلد فنی LTR است."""

    __tablename__ = "symbols"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    asset_class: Mapped[Optional[str]] = mapped_column(String(50))
    pip_size: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))
    contract_size: Mapped[Optional[float]] = mapped_column(Numeric(18, 4))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    trades: Mapped[list["Trade"]] = relationship(back_populates="symbol")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Symbol {self.name}>"
