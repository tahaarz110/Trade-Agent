from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, UUIDPKMixin
from app.models.enums import SampleQuality
from app.models.types import portable_enum


class FeatureSnapshot(UUIDPKMixin, Base):
    """ویژگی‌های مهندسی‌شده هر معامله (weekday, hour, session, killzone,
    duration, risk_compliance, checklist_compliance, ...). خروجی
    Feature Engineering Engine طبق پرامپت مادر."""

    __tablename__ = "feature_snapshots"
    __table_args__ = (UniqueConstraint("trade_id", name="uq_feature_snapshots_trade"),)

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), nullable=False
    )
    features: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[Optional[str]] = mapped_column(String(30))
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class InsightSegment(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """یک تعریف بخش‌بندی (ترکیبی از فیلترها) که Edge Explorer/Pattern
    Discovery روی آن محاسبه می‌شوند."""

    __tablename__ = "insight_segments"

    name: Mapped[str] = mapped_column(String(300), nullable=False)
    definition: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    metrics: Mapped[list["InsightMetric"]] = relationship(
        back_populates="segment", cascade="all, delete-orphan"
    )
    patterns: Mapped[list["InsightPattern"]] = relationship(
        back_populates="segment", cascade="all, delete-orphan"
    )


class InsightMetric(UUIDPKMixin, Base):
    """مقدار قطعی یک متریک آماری (win_rate, avg_r, profit_factor, ...)
    برای یک scope مشخص (کلی/حساب/بخش)."""

    __tablename__ = "insight_metrics"

    metric_key: Mapped[str] = mapped_column(String(100), nullable=False)
    scope: Mapped[str] = mapped_column(String(30), nullable=False, default="global")
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE")
    )
    segment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("insight_segments.id", ondelete="CASCADE")
    )
    value: Mapped[Optional[float]] = mapped_column(Numeric(24, 8))
    trade_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    segment: Mapped[Optional["InsightSegment"]] = relationship(back_populates="metrics")


class InsightPattern(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """الگوی کشف‌شده توسط Pattern Discovery Engine، همراه با شواهد و
    کیفیت نمونه (طبق الزامات Statistical Safety پرامپت مادر)."""

    __tablename__ = "insight_patterns"

    segment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("insight_segments.id", ondelete="SET NULL")
    )
    pattern_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    trade_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    win_rate: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    avg_r: Mapped[Optional[float]] = mapped_column(Numeric(9, 4))
    reliability: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    sample_quality: Mapped[Optional[SampleQuality]] = mapped_column(
        portable_enum(SampleQuality, "sample_quality")
    )
    evidence: Mapped[Optional[dict]] = mapped_column(JSONB)

    segment: Mapped[Optional["InsightSegment"]] = relationship(back_populates="patterns")
    validations: Mapped[list["InsightValidation"]] = relationship(
        back_populates="pattern", cascade="all, delete-orphan"
    )


class InsightValidation(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """نتیجه اعتبارسنجی یک الگو (حداقل نمونه، هموارسازی بیزی، آزمون
    out-of-sample/walk-forward) طبق Validation Engine."""

    __tablename__ = "insight_validations"

    pattern_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("insight_patterns.id", ondelete="CASCADE"), nullable=False
    )
    validation_method: Mapped[str] = mapped_column(String(100), nullable=False)
    result: Mapped[Optional[dict]] = mapped_column(JSONB)
    passed: Mapped[Optional[bool]] = mapped_column(Boolean)

    pattern: Mapped["InsightPattern"] = relationship(back_populates="validations")
