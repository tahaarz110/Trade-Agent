from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- ThemeSetting ------------------------------------------------------------------
class ThemeSettingUpdate(BaseModel):
    theme_name: Optional[str] = Field(default=None, max_length=50)
    font_family: Optional[str] = Field(default=None, max_length=100)
    font_size: Optional[str] = Field(default=None, max_length=20)
    density: Optional[str] = Field(default=None, max_length=20)
    primary_color: Optional[str] = Field(default=None, max_length=20)
    settings: Optional[dict[str, Any]] = None


class ThemeSettingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    theme_name: str
    font_family: Optional[str] = None
    font_size: Optional[str] = None
    density: Optional[str] = None
    primary_color: Optional[str] = None
    settings: Optional[dict[str, Any]] = None
    updated_at: datetime


# --- UITab ---------------------------------------------------------------------
class UITabBase(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=150)
    icon: Optional[str] = None
    sort_order: int = 0


class UITabCreate(UITabBase):
    pass


class UITabUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    icon: Optional[str] = None
    is_visible: Optional[bool] = None
    sort_order: Optional[int] = None


class UITabRead(UITabBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_visible: bool
