from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FieldType


# --- FieldSection ------------------------------------------------------------
class FieldSectionBase(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    sort_order: int = 0


class FieldSectionCreate(FieldSectionBase):
    pass


class FieldSectionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class FieldSectionRead(FieldSectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


# --- FieldOption ---------------------------------------------------------------
class FieldOptionBase(BaseModel):
    value: str = Field(min_length=1, max_length=150)
    label: str = Field(min_length=1, max_length=200)
    color: Optional[str] = None
    sort_order: int = 0


class FieldOptionCreate(FieldOptionBase):
    field_id: uuid.UUID


class FieldOptionUpdate(BaseModel):
    label: Optional[str] = Field(default=None, min_length=1, max_length=200)
    color: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class FieldOptionRead(FieldOptionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    field_id: uuid.UUID
    is_active: bool


# --- FieldDefinition -----------------------------------------------------------
class FieldDefinitionBase(BaseModel):
    section_id: uuid.UUID
    slug: str = Field(min_length=1, max_length=150)
    title: str = Field(min_length=1, max_length=200)
    field_type: FieldType
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    default_value: Optional[str] = None
    unit: Optional[str] = None
    is_required: bool = False
    rtl_display: bool = True
    ltr_input: bool = False
    show_in_form: bool = True
    show_in_table: bool = False
    show_in_detail: bool = True
    filterable: bool = False
    analytic_enabled: bool = False
    ai_enabled: bool = False
    validation_rules: Optional[dict[str, Any]] = None
    sort_order: int = 0


class FieldDefinitionCreate(FieldDefinitionBase):
    options: Optional[list[str]] = Field(
        default=None,
        description="فهرست ساده مقادیر گزینه برای فیلدهای انتخابی (اختیاری، معادل چند بار فراخوانی افزودن گزینه)",
    )


class FieldDefinitionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    default_value: Optional[str] = None
    unit: Optional[str] = None
    is_required: Optional[bool] = None
    is_active: Optional[bool] = None
    rtl_display: Optional[bool] = None
    ltr_input: Optional[bool] = None
    show_in_form: Optional[bool] = None
    show_in_table: Optional[bool] = None
    show_in_detail: Optional[bool] = None
    filterable: Optional[bool] = None
    analytic_enabled: Optional[bool] = None
    ai_enabled: Optional[bool] = None
    validation_rules: Optional[dict[str, Any]] = None
    sort_order: Optional[int] = None


class FieldDefinitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    section_id: uuid.UUID
    slug: str
    title: str
    field_type: FieldType
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    default_value: Optional[str] = None
    unit: Optional[str] = None
    is_required: bool
    is_system: bool
    is_active: bool
    rtl_display: bool
    ltr_input: bool
    show_in_form: bool
    show_in_table: bool
    show_in_detail: bool
    filterable: bool
    analytic_enabled: bool
    ai_enabled: bool
    validation_rules: Optional[dict[str, Any]] = None
    sort_order: int
    created_at: datetime
    updated_at: datetime
    options: list[FieldOptionRead] = []


# --- Reorder ------------------------------------------------------------------
class ReorderItem(BaseModel):
    id: uuid.UUID
    sort_order: int


class ReorderRequest(BaseModel):
    items: list[ReorderItem]
