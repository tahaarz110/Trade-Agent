from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- ChecklistItem ---------------------------------------------------------------
class ChecklistItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: Optional[str] = None
    is_required: bool = False
    sort_order: int = 0


class ChecklistItemCreate(ChecklistItemBase):
    template_id: uuid.UUID


class ChecklistItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    description: Optional[str] = None
    is_required: Optional[bool] = None
    sort_order: Optional[int] = None


class ChecklistItemRead(ChecklistItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    template_id: uuid.UUID


# --- ChecklistTemplate -----------------------------------------------------------
class ChecklistTemplateBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    is_default: bool = False


class ChecklistTemplateCreate(ChecklistTemplateBase):
    pass


class ChecklistTemplateUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class ChecklistTemplateRead(ChecklistTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: list[ChecklistItemRead] = []
