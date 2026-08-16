from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.field import FieldOption
from app.repositories.field import FieldDefinitionRepository, FieldOptionRepository
from app.schemas.field import FieldOptionCreate, FieldOptionUpdate, ReorderRequest
from app.services import NotFoundError, ValidationAppError


class FieldOptionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FieldOptionRepository(db)
        self.field_repo = FieldDefinitionRepository(db)

    def create(self, payload: FieldOptionCreate) -> FieldOption:
        field = self.field_repo.get(payload.field_id)
        if not field:
            raise NotFoundError("فیلد پویا", payload.field_id)

        option = FieldOption(**payload.model_dump())
        self.repo.add(option)
        self.db.commit()
        self.db.refresh(option)
        return option

    def get(self, option_id: uuid.UUID) -> FieldOption:
        option = self.repo.get(option_id)
        if not option:
            raise NotFoundError("گزینه فیلد", option_id)
        return option

    def list_for_field(self, field_id: uuid.UUID) -> list[FieldOption]:
        return (
            self.db.query(FieldOption)
            .filter_by(field_id=field_id)
            .order_by(FieldOption.sort_order.asc())
            .all()
        )

    def update(self, option_id: uuid.UUID, payload: FieldOptionUpdate) -> FieldOption:
        option = self.get(option_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(option, key, value)
        self.db.commit()
        self.db.refresh(option)
        return option

    def set_active(self, option_id: uuid.UUID, is_active: bool) -> FieldOption:
        option = self.get(option_id)
        option.is_active = is_active
        self.db.commit()
        self.db.refresh(option)
        return option

    def reorder(self, field_id: uuid.UUID, payload: ReorderRequest) -> list[FieldOption]:
        ids = [item.id for item in payload.items]
        options = (
            self.db.query(FieldOption)
            .filter(FieldOption.id.in_(ids), FieldOption.field_id == field_id)
            .all()
        )
        found_ids = {o.id for o in options}
        missing = set(ids) - found_ids
        if missing:
            raise NotFoundError("گزینه فیلد", next(iter(missing)))

        order_map = {item.id: item.sort_order for item in payload.items}
        for option in options:
            option.sort_order = order_map[option.id]
        self.db.commit()
        return self.list_for_field(field_id)

    def delete(self, option_id: uuid.UUID) -> None:
        option = self.get(option_id)
        if self.repo.is_option_value_used(option.field_id, option.value):
            raise ValidationAppError(
                "این گزینه در معاملات قبلی استفاده شده و برای حفظ یکپارچگی تاریخچه "
                "قابل حذف نیست؛ به‌جای حذف، آن را غیرفعال کنید"
            )
        self.repo.delete(option)
        self.db.commit()
