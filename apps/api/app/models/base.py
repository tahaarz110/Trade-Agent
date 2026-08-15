"""Mixin های مشترک بین همه مدل‌های SQLAlchemy.

- UUIDPKMixin: کلید اصلی UUID (طبق الزام فاز ۱: «از UUID برای کلید اصلی
  استفاده شود»)
- TimestampMixin: created_at / updated_at از نوع TIMESTAMPTZ
- CreatedAtOnlyMixin: برای جدول‌های append-only که نیازی به updated_at ندارند
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPKMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CreatedAtOnlyMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
