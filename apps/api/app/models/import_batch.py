from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, UUIDPKMixin


class ImportBatch(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """یک اجرای ایمپورت (MT5/MT4 EA Bridge/CSV) به همراه لاگ و آمار."""

    __tablename__ = "import_batches"
    __table_args__ = (
        # برای فهرست «تاریخچه ایمپورت‌های این حساب» (فاز ۶) در مقیاس بالا.
        Index("ix_import_batches_account_id", "account_id"),
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        # RESTRICT نه CASCADE: طبق همان اصلی که برای trades.account_id
        # رفع شد، حذف یک حساب هرگز نباید تاریخچه ایمپورت آن را بی‌صدا
        # نابود کند.
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")

    total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    needs_review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    log: Mapped[Optional[dict]] = mapped_column(JSONB)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
