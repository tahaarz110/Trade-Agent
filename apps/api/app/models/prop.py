from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, TimestampMixin, UUIDPKMixin
from app.models.enums import PropRuleType
from app.models.types import portable_enum


class PropRule(UUIDPKMixin, TimestampMixin, Base):
    """قانون حساب پراپ (حداکثر ضرر روزانه، حداکثر افت سرمایه، قانون
    ثبات، محدودیت خبر، نگه‌داشتن آخر هفته، حداکثر تعداد معامله روزانه).

    اگر account_id خالی باشد، رکورد یک «قالب پیش‌فرض» است که هنگام
    ساخت حساب پراپ جدید می‌توان از روی آن یک نمونه اختصاصی ساخت."""

    __tablename__ = "prop_rules"

    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE")
    )
    rule_type: Mapped[PropRuleType] = mapped_column(
        portable_enum(PropRuleType, "prop_rule_type"), nullable=False
    )
    threshold_value: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    threshold_percent: Mapped[Optional[float]] = mapped_column(Numeric(9, 4))
    is_template: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    config: Mapped[Optional[dict]] = mapped_column(JSONB)

    account: Mapped[Optional["Account"]] = relationship(back_populates="prop_rules")
    violations: Mapped[list["PropViolation"]] = relationship(
        back_populates="prop_rule", cascade="all, delete-orphan"
    )


class PropViolation(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """تخلف ثبت‌شده از یک قانون پراپ."""

    __tablename__ = "prop_violations"

    prop_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prop_rules.id", ondelete="CASCADE"), nullable=False
    )
    trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="SET NULL")
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    violation_date: Mapped[Optional[date]] = mapped_column(Date)
    details: Mapped[Optional[dict]] = mapped_column(JSONB)
    severity: Mapped[Optional[str]] = mapped_column(String(30))

    prop_rule: Mapped["PropRule"] = relationship(back_populates="violations")
