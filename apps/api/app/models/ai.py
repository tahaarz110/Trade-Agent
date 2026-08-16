from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, UUIDPKMixin
from app.models.enums import AIJobStatus
from app.models.types import portable_enum


class AIInsight(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """خروجی راوی AI یا موتور تحلیلی که برای نمایش/بایگانی ذخیره شده.
    توجه: خودِ اعداد باید قبلاً به‌صورت قطعی محاسبه شده باشند؛ این جدول
    صرفاً روایت/توضیح متنی را نگه می‌دارد."""

    __tablename__ = "ai_insights"

    trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    insight_type: Mapped[Optional[str]] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="deterministic")
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)


class AIJob(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """صف کارهای پس‌زمینه (تحلیل سنگین، تولید گزارش، فراخوانی راوی AI)."""

    __tablename__ = "ai_jobs"

    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[AIJobStatus] = mapped_column(
        portable_enum(AIJobStatus, "ai_job_status"), nullable=False, default=AIJobStatus.PENDING
    )
    payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    result: Mapped[Optional[dict]] = mapped_column(JSONB)
    error: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
