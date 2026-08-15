from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import UUIDPKMixin


class UITab(UUIDPKMixin, Base):
    """تب‌ها/آیتم‌های سایدبار قابل مدیریت توسط کاربر."""

    __tablename__ = "ui_tabs"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100))
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ThemeSetting(UUIDPKMixin, Base):
    """تنظیمات ظاهری (تم، فونت، اندازه فونت، تراکم چیدمان)."""

    __tablename__ = "theme_settings"

    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, default="default")
    theme_name: Mapped[str] = mapped_column(String(50), nullable=False, default="light")
    font_family: Mapped[Optional[str]] = mapped_column(String(100))
    font_size: Mapped[Optional[str]] = mapped_column(String(20))
    density: Mapped[Optional[str]] = mapped_column(String(20))
    primary_color: Mapped[Optional[str]] = mapped_column(String(20))
    settings: Mapped[Optional[dict]] = mapped_column(JSONB)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
