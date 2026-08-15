from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, UUIDPKMixin
from app.models.enums import PeriodType, RiskLevel
from app.models.types import portable_enum


class BehaviorScore(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """امتیاز ریسک رفتاری در سطح معامله/روز/هفته (FOMO، معامله انتقامی،
    حجم بیش از حد، معامله خارج از سشن و...)."""

    __tablename__ = "behavior_scores"

    trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE")
    )
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE")
    )
    period_type: Mapped[PeriodType] = mapped_column(
        portable_enum(PeriodType, "behavior_period_type"), nullable=False
    )
    period_start: Mapped[Optional[date]] = mapped_column(Date)
    score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        portable_enum(RiskLevel, "behavior_risk_level"), nullable=False
    )
    factors: Mapped[Optional[dict]] = mapped_column(JSONB)


class DisciplineScore(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """امتیاز انضباط (مستقل از سود/زیان): تکمیل چک‌لیست، رعایت پلن،
    عدم جابجایی حد ضرر، رعایت ریسک، انجام بازبینی."""

    __tablename__ = "discipline_scores"

    trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE")
    )
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE")
    )
    period_type: Mapped[PeriodType] = mapped_column(
        portable_enum(PeriodType, "discipline_period_type"), nullable=False
    )
    period_start: Mapped[Optional[date]] = mapped_column(Date)
    score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    factors: Mapped[Optional[dict]] = mapped_column(JSONB)
