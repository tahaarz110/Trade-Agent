from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.field import FieldSection
from app.repositories.field import FieldSectionRepository
from app.schemas.field import FieldSectionCreate, FieldSectionUpdate, ReorderRequest
from app.services import ConflictError, NotFoundError, ValidationAppError


class FieldSectionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FieldSectionRepository(db)

    def create(self, payload: FieldSectionCreate) -> FieldSection:
        section = FieldSection(**payload.model_dump(), is_system=False)
        try:
            self.repo.add(section)
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(f"سکشنی با کلید «{payload.key}» از قبل وجود دارد") from exc
        self.db.refresh(section)
        return section

    def get(self, section_id: uuid.UUID) -> FieldSection:
        section = self.repo.get(section_id)
        if not section:
            raise NotFoundError("سکشن فیلد", section_id)
        return section

    def list(self, *, include_inactive: bool = True) -> list[FieldSection]:
        query = self.db.query(FieldSection).order_by(FieldSection.sort_order.asc())
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.all()

    def update(self, section_id: uuid.UUID, payload: FieldSectionUpdate) -> FieldSection:
        section = self.get(section_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(section, key, value)
        self.db.commit()
        self.db.refresh(section)
        return section

    def set_active(self, section_id: uuid.UUID, is_active: bool) -> FieldSection:
        section = self.get(section_id)
        section.is_active = is_active
        self.db.commit()
        self.db.refresh(section)
        return section

    def reorder(self, payload: ReorderRequest) -> list[FieldSection]:
        ids = [item.id for item in payload.items]
        sections = self.db.query(FieldSection).filter(FieldSection.id.in_(ids)).all()
        found_ids = {s.id for s in sections}
        missing = set(ids) - found_ids
        if missing:
            raise NotFoundError("سکشن فیلد", next(iter(missing)))

        order_map = {item.id: item.sort_order for item in payload.items}
        for section in sections:
            section.sort_order = order_map[section.id]
        self.db.commit()
        return self.list()

    def delete(self, section_id: uuid.UUID) -> None:
        section = self.get(section_id)
        if section.is_system:
            raise ValidationAppError("سکشن‌های سیستمی قابل حذف نیستند؛ می‌توانید آن را غیرفعال کنید")
        if self.repo.has_fields_with_historical_values(section_id):
            raise ValidationAppError(
                "این سکشن شامل فیلدی است که در معاملات قبلی مقدار ثبت‌شده دارد؛ "
                "به‌جای حذف، سکشن را غیرفعال کنید"
            )
        self.repo.delete(section)
        self.db.commit()
