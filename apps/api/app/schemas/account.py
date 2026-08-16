from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AccountType


class AccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    account_type: AccountType
    broker: Optional[str] = Field(default=None, max_length=200)
    currency: str = Field(default="USD", max_length=10)
    initial_balance: Optional[Decimal] = None
    current_balance: Optional[Decimal] = None
    leverage: Optional[Decimal] = None
    is_active: bool = True
    notes: Optional[str] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    account_type: Optional[AccountType] = None
    broker: Optional[str] = None
    currency: Optional[str] = None
    initial_balance: Optional[Decimal] = None
    current_balance: Optional[Decimal] = None
    leverage: Optional[Decimal] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class AccountRead(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
