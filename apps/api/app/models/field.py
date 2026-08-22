from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.enums import FieldType
from app.models.types import portable_enum


class FieldSection(UUIDPKMixin, TimestampMixin, Base):
    """سکشن‌های فرم معامله (پیش‌فرض یا سفارشی کاربر)."""

    __tablename__ = "field_sections"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    fields: Mapped[list["FieldDefinition"]] = relationship(
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="FieldDefinition.sort_order",
    )


class FieldDefinition(UUIDPKMixin, TimestampMixin, Base):
    """تعریف یک فیلد پویا (سیستمی یا سفارشی). اگر analytic_enabled=true
    باشد، مقدار آن باید در تحلیل‌ها، فیلترها، بینش‌ها و گزارش‌ها لحاظ شود."""

    __tablename__ = "field_definitions"
    __table_args__ = (UniqueConstraint("slug", name="uq_field_definitions_slug"),)

    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("field_sections.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False)
    field_type: Mapped[FieldType] = mapped_column(
        portable_enum(FieldType, "field_type"), nullable=False
    )
    placeholder: Mapped[Optional[str]] = mapped_column(String(300))
    help_text: Mapped[Optional[str]] = mapped_column(Text)
    default_value: Mapped[Optional[str]] = mapped_column(Text)
    unit: Mapped[Optional[str]] = mapped_column(String(50))

    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    rtl_display: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ltr_input: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    show_in_form: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    show_in_table: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    show_in_detail: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    filterable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    analytic_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    validation_rules: Mapped[Optional[dict]] = mapped_column(JSONB)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    section: Mapped["FieldSection"] = relationship(back_populates="fields")
    options: Mapped[list["FieldOption"]] = relationship(
        back_populates="field", cascade="all, delete-orphan", order_by="FieldOption.sort_order"
    )
    values: Mapped[list["TradeFieldValue"]] = relationship(
        back_populates="field", cascade="all, delete-orphan"
    )


class FieldOption(UUIDPKMixin, Base):
    """گزینه‌های انتخابی برای فیلدهای select/radio/checkbox/multi_select."""

    __tablename__ = "field_options"
    __table_args__ = (Index("ix_field_options_field_id", "field_id"),)

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("field_definitions.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[str] = mapped_column(String(150), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    field: Mapped["FieldDefinition"] = relationship(back_populates="options")


class TradeFieldValue(UUIDPKMixin, TimestampMixin, Base):
    """مقدار یک فیلد پویا برای یک معامله مشخص. برای پشتیبانی از انواع
    مختلف فیلد، چند ستون تایپ‌شده جداگانه نگه‌داری می‌شود (به‌جای فقط
    JSON) تا کوئری‌های تحلیلی (گروه‌بندی، بین‌بندی عددی و...) در
    PostgreSQL/DuckDB بهینه بمانند."""

    __tablename__ = "trade_field_values"
    __table_args__ = (
        UniqueConstraint("trade_id", "field_id", name="uq_trade_field_values_trade_field"),
        # ایندکس مستقل روی field_id: محدودیت یکتای بالا فقط برای کوئری‌های
        # trade_id-first بهینه است (مثل «مقادیر این معامله»)؛ عملیات
        # زیر روی field_id به‌تنهایی فیلتر می‌کنند (بررسی حذف مخرب فیلد،
        # بررسی استفاده از گزینه، فیلتر داینامیک معاملات بر اساس فیلد)
        # و بدون این ایندکس در حجم بالا (صدها هزار معامله طبق پرامپت
        # مادر) به اسکن کامل جدول می‌انجامند.
        Index("ix_trade_field_values_field_id", "field_id"),
        # ایندکس GIN برای کوئری‌های containment روی value_json (مقادیر
        # چندانتخابی) که در بررسی استفاده از گزینه به کار می‌رود.
        Index("ix_trade_field_values_value_json_gin", "value_json", postgresql_using="gin"),
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), nullable=False
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("field_definitions.id", ondelete="CASCADE"), nullable=False
    )

    value_text: Mapped[Optional[str]] = mapped_column(Text)
    value_number: Mapped[Optional[float]] = mapped_column(Numeric(24, 8))
    value_boolean: Mapped[Optional[bool]] = mapped_column(Boolean)
    value_date: Mapped[Optional[date]] = mapped_column(Date)
    value_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # برای multi_select و مقادیر ساختاریافته دیگر
    value_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    trade: Mapped["Trade"] = relationship(back_populates="field_values")
    field: Mapped["FieldDefinition"] = relationship(back_populates="values")
