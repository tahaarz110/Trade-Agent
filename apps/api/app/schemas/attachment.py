from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trade_id: uuid.UUID
    file_name: str
    file_path: str
    thumbnail_path: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    caption: Optional[str] = None
    sort_order: int
    created_at: datetime
