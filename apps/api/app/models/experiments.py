from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, TimestampMixin, UUIDPKMixin
from app.models.enums import ExperimentStatus, HypothesisStatus
from app.models.types import portable_enum


class Hypothesis(UUIDPKMixin, TimestampMixin, Base):
    """فرضیه‌ای که کاربر مطرح می‌کند، مثلاً «اگر فقط در سشن لندن معامله
    کنم نتایجم بهتر می‌شود»."""

    __tablename__ = "hypotheses"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[HypothesisStatus] = mapped_column(
        portable_enum(HypothesisStatus, "hypothesis_status"),
        nullable=False,
        default=HypothesisStatus.DRAFT,
    )

    experiments: Mapped[list["Experiment"]] = relationship(back_populates="hypothesis")


class Experiment(UUIDPKMixin, TimestampMixin, Base):
    """آزمایش فعال برای پیگیری معاملات آینده منطبق با شرایط فرضیه و
    مقایسه با baseline. طبق پرامپت مادر باید حداقل نمونه رعایت شود."""

    __tablename__ = "experiments"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    hypothesis_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hypotheses.id", ondelete="SET NULL")
    )
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[ExperimentStatus] = mapped_column(
        portable_enum(ExperimentStatus, "experiment_status"),
        nullable=False,
        default=ExperimentStatus.PENDING,
    )
    min_sample_size: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    concluded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    hypothesis: Mapped[Optional["Hypothesis"]] = relationship(back_populates="experiments")
    results: Mapped[list["ExperimentResult"]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )


class ExperimentResult(UUIDPKMixin, Base):
    """آخرین/تاریخچه نتیجه محاسبه‌شده یک آزمایش در مقایسه با baseline."""

    __tablename__ = "experiment_results"

    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False
    )
    trade_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    win_rate: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    avg_r: Mapped[Optional[float]] = mapped_column(Numeric(9, 4))
    baseline_win_rate: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    baseline_avg_r: Mapped[Optional[float]] = mapped_column(Numeric(9, 4))
    conclusion: Mapped[Optional[str]] = mapped_column(Text)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    experiment: Mapped["Experiment"] = relationship(back_populates="results")


class PreTradeCheck(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """ارزیابی دروازه پیش از معامله: شرایط فعلی در برابر شواهد تاریخی."""

    __tablename__ = "pre_trade_checks"

    trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="SET NULL")
    )
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL")
    )
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    historical_win_rate: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    historical_avg_r: Mapped[Optional[float]] = mapped_column(Numeric(9, 4))
    sample_size: Mapped[Optional[int]] = mapped_column(Integer)
    warnings: Mapped[Optional[dict]] = mapped_column(JSONB)
