from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TradeDirection, TradeStatus


class TradeBase(BaseModel):
    account_id: uuid.UUID
    symbol_id: uuid.UUID
    direction: TradeDirection
    status: TradeStatus = TradeStatus.OPEN

    entry_time: datetime
    exit_time: Optional[datetime] = None

    entry_price: Decimal
    exit_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None

    volume: Decimal
    commission: Decimal = Decimal("0")
    swap: Decimal = Decimal("0")

    gross_profit: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None
    risk_amount: Optional[Decimal] = None
    risk_percent: Optional[Decimal] = None
    r_multiple: Optional[Decimal] = None
    pips: Optional[Decimal] = None

    balance_before: Optional[Decimal] = None
    balance_after: Optional[Decimal] = None

    external_id: Optional[str] = None
    broker_ticket: Optional[str] = None
    position_id: Optional[str] = None
    magic_number: Optional[str] = None

    needs_review: bool = False
    review_status: Optional[str] = None


class TradeCreate(TradeBase):
    # مقادیر فیلدهای پویا: کلید = slug فیلد، مقدار = مقدار خام کاربر.
    # سرویس لایه، این مقادیر را با field_definitions تطبیق و به ستون
    # تایپ‌شده مناسب در trade_field_values ذخیره می‌کند.
    custom_fields: dict[str, Any] = Field(default_factory=dict)


class TradeUpdate(BaseModel):
    direction: Optional[TradeDirection] = None
    status: Optional[TradeStatus] = None
    exit_time: Optional[datetime] = None
    exit_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    commission: Optional[Decimal] = None
    swap: Optional[Decimal] = None
    gross_profit: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None
    risk_amount: Optional[Decimal] = None
    risk_percent: Optional[Decimal] = None
    r_multiple: Optional[Decimal] = None
    pips: Optional[Decimal] = None
    balance_after: Optional[Decimal] = None
    needs_review: Optional[bool] = None
    review_status: Optional[str] = None
    custom_fields: Optional[dict[str, Any]] = None


class TradeRead(TradeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    duration_minutes: Optional[int] = None
    import_source: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TradeFieldValueRead(BaseModel):
    field_slug: str
    field_title: str
    field_type: str
    value: Any


class TradeDetailRead(TradeRead):
    """پاسخ endpoint جزئیات معامله: فیلدهای اصلی + مقادیر فیلدهای پویا."""

    custom_fields: list[TradeFieldValueRead] = Field(default_factory=list)
