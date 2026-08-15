from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, TimestampMixin, UUIDPKMixin


class MistakeTag(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """برچسب قابل‌انتخاب اشتباه (برای پرهیز از تایپ آزاد و امکان تحلیل)."""

    __tablename__ = "mistake_tags"

    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    costs: Mapped[list["MistakeCost"]] = relationship(
        back_populates="mistake_tag", cascade="all, delete-orphan"
    )


class MistakeCost(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """هزینه یک اشتباه مشخص روی یک معامله مشخص (بر حسب R، مبلغ، و درصد
    از کل زیان) — خروجی Mistake Cost Engine."""

    __tablename__ = "mistake_costs"
    __table_args__ = (
        UniqueConstraint("trade_id", "mistake_tag_id", name="uq_mistake_costs_trade_tag"),
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), nullable=False
    )
    mistake_tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mistake_tags.id", ondelete="CASCADE"), nullable=False
    )
    cost_r: Mapped[Optional[float]] = mapped_column(Numeric(9, 4))
    cost_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    cost_percent: Mapped[Optional[float]] = mapped_column(Numeric(9, 4))

    trade: Mapped["Trade"] = relationship(back_populates="mistake_costs")
    mistake_tag: Mapped["MistakeTag"] = relationship(back_populates="costs")


class Lesson(UUIDPKMixin, TimestampMixin, Base):
    """درس قابل‌استفاده مجدد، استخراج‌شده از اشتباهات/یادداشت‌های تکراری."""

    __tablename__ = "lessons"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    recurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    links: Mapped[list["LessonLink"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan"
    )


class LessonLink(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """پیوند یک درس به معامله/برچسب اشتباه/الگوی بینش (polymorphic،
    از طریق linked_type + linked_id)."""

    __tablename__ = "lesson_links"

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False
    )
    linked_type: Mapped[str] = mapped_column(String(50), nullable=False)
    linked_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    lesson: Mapped["Lesson"] = relationship(back_populates="links")
