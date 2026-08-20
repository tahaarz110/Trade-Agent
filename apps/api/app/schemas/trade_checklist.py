from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class ChecklistAnswerInput(BaseModel):
    item_id: uuid.UUID
    checked: bool = False
    note: Optional[str] = None


class TradeChecklistUpdate(BaseModel):
    """بدنه PUT /trades/{trade_id}/checklist.

    اگر checklist_template_id برابر None باشد، یعنی هیچ قالبی به این
    معامله اختصاص داده نشود (و اختصاص قبلی پاک شود، بدون حذف پاسخ‌های
    تاریخی — طبق الزام فاز ۵.۵)."""

    checklist_template_id: Optional[uuid.UUID] = None
    answers: list[ChecklistAnswerInput] = Field(default_factory=list)


class TradeChecklistItemRead(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    is_required: bool
    sort_order: int
    is_active: bool
    checked: bool
    note: Optional[str] = None


class TradeChecklistRead(BaseModel):
    """پاسخ کامل GET/PUT /trades/{trade_id}/checklist."""

    trade_id: uuid.UUID
    checklist_template_id: Optional[uuid.UUID] = None
    checklist_template_title: Optional[str] = None
    items: list[TradeChecklistItemRead] = Field(default_factory=list)

    total_items: int = 0
    checked_items: int = 0
    required_items: int = 0
    required_checked_items: int = 0
    required_missing_items: list[str] = Field(default_factory=list)
    score_percent: Optional[float] = None


class TradeChecklistSummary(BaseModel):
    """خلاصه سبک برای تعبیه در پاسخ جزئیات معامله (بدون سنگین کردن آن)."""

    has_checklist: bool = False
    checklist_template_title: Optional[str] = None
    checklist_score_percent: Optional[float] = None
    required_missing_count: int = 0
