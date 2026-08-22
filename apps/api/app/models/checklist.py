from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class ChecklistTemplate(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "checklist_templates"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    items: Mapped[list["ChecklistItem"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="ChecklistItem.sort_order",
    )


class ChecklistItem(UUIDPKMixin, Base):
    __tablename__ = "checklist_items"
    __table_args__ = (Index("ix_checklist_items_template_id", "template_id"),)

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("checklist_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # فاز ۵.۵ (اصلاحی): برای غیرفعال‌سازی به‌جای حذف مخرب آیتم‌هایی که
    # پاسخ تاریخی دارند، و رد پاسخ‌دهی تازه به آیتم‌های غیرفعال.
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    template: Mapped["ChecklistTemplate"] = relationship(back_populates="items")
    answers: Mapped[list["TradeChecklistAnswer"]] = relationship(
        back_populates="checklist_item", cascade="all, delete-orphan"
    )


class TradeChecklistAnswer(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "trade_checklist_answers"
    __table_args__ = (
        UniqueConstraint(
            "trade_id", "checklist_item_id", name="uq_trade_checklist_answers_trade_item"
        ),
        # برای بررسی «آیا این آیتم پاسخ تاریخی دارد» (چک محافظت حذف)
        # که به‌تنهایی روی checklist_item_id فیلتر می‌کند و از پیشوند
        # چپ محدودیت یکتای بالا (trade_id) بهره نمی‌برد.
        Index("ix_trade_checklist_answers_checklist_item_id", "checklist_item_id"),
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), nullable=False
    )
    checklist_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("checklist_items.id", ondelete="CASCADE"), nullable=False
    )
    is_checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    note: Mapped[Optional[str]] = mapped_column(Text)

    trade: Mapped["Trade"] = relationship(back_populates="checklist_answers")
    checklist_item: Mapped["ChecklistItem"] = relationship(back_populates="answers")
