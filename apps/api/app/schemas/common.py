from __future__ import annotations

import uuid

from pydantic import BaseModel


class ReorderItem(BaseModel):
    id: uuid.UUID
    sort_order: int


class ReorderRequest(BaseModel):
    items: list[ReorderItem]
