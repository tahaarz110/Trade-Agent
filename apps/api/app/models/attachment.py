from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, UUIDPKMixin


class Attachment(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """پیوست تصویری/فایلی یک معامله (اسکرین‌شات چارت و غیره)."""

    __tablename__ = "attachments"
    __table_args__ = (
        # بدون این ایندکس، نمایش گالری تصاویر هر معامله (فراخوانی‌شده
        # در هر بار باز شدن مودال جزئیات) با رشد جدول attachments در
        # مقیاس صدها هزار معامله به اسکن کامل جدول تبدیل می‌شود.
        Index("ix_attachments_trade_id", "trade_id"),
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    # مسیر تصویر بندانگشتی (thumbnail) تولیدشده توسط سرویس پیوست‌ها؛
    # برای فایل‌های غیرتصویری خالی می‌ماند. افزوده‌شده در فاز ۲.
    thumbnail_path: Mapped[Optional[str]] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    caption: Mapped[Optional[str]] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    trade: Mapped["Trade"] = relationship(back_populates="attachments")
