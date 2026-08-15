from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, UUIDPKMixin


class AuditLog(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """رکورد ممیزی برای عملیات حساس (ایجاد/ویرایش/حذف/بازیابی بکاپ و...)."""

    __tablename__ = "audit_logs"

    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor: Mapped[Optional[str]] = mapped_column(String(150))
    changes: Mapped[Optional[dict]] = mapped_column(JSONB)
