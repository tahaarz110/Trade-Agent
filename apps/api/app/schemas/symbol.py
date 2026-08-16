from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SymbolBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    asset_class: Optional[str] = Field(default=None, max_length=50)
    pip_size: Optional[Decimal] = None
    contract_size: Optional[Decimal] = None
    is_active: bool = True


class SymbolCreate(SymbolBase):
    pass


class SymbolUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    display_name: Optional[str] = None
    asset_class: Optional[str] = None
    pip_size: Optional[Decimal] = None
    contract_size: Optional[Decimal] = None
    is_active: Optional[bool] = None


class SymbolRead(SymbolBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
