from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, UUIDPKMixin
from app.models.enums import AlertSeverity, ReportType
from app.models.types import portable_enum


class Alert(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """هشدار سیستمی (نقض قانون پراپ، ریسک رفتاری بالا، و غیره)."""

    __tablename__ = "alerts"

    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(
        portable_enum(AlertSeverity, "alert_severity"), nullable=False, default=AlertSeverity.INFO
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text)
    related_type: Mapped[Optional[str]] = mapped_column(String(50))
    related_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ReportRun(UUIDPKMixin, Base):
    """یک اجرای تولید گزارش قالب‌محور فارسی (بدون LLM)."""

    __tablename__ = "report_runs"

    report_type: Mapped[ReportType] = mapped_column(
        portable_enum(ReportType, "report_type"), nullable=False
    )
    period_start: Mapped[Optional[date]] = mapped_column(Date)
    period_end: Mapped[Optional[date]] = mapped_column(Date)
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL")
    )
    content: Mapped[Optional[str]] = mapped_column(Text)
    data: Mapped[Optional[dict]] = mapped_column(JSONB)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
