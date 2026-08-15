from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import CreatedAtOnlyMixin, UUIDPKMixin


class TextTerm(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """کلیدواژه استخراج‌شده از یادداشت‌های معاملات (TF-IDF/hazm)."""

    __tablename__ = "text_terms"

    term: Mapped[str] = mapped_column(String(200), nullable=False)
    normalized_term: Mapped[Optional[str]] = mapped_column(String(200))
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    tf_idf_score: Mapped[Optional[float]] = mapped_column(Numeric(12, 8))


class TextTheme(UUIDPKMixin, CreatedAtOnlyMixin, Base):
    """تم تکرارشونده استخراج‌شده از یادداشت‌ها و پیوند آن به برچسب اشتباه."""

    __tablename__ = "text_themes"

    theme_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    related_terms: Mapped[Optional[dict]] = mapped_column(JSONB)
    mistake_tag_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mistake_tags.id", ondelete="SET NULL")
    )
