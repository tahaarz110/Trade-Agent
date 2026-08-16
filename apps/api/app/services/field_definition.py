from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.field import FieldDefinition, FieldOption
from app.repositories.field import FieldDefinitionRepository, FieldSectionRepository
from app.schemas.field import FieldDefinitionCreate, FieldDefinitionUpdate, ReorderRequest
from app.services import ConflictError, NotFoundError, ValidationAppError


class FieldDefinitionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FieldDefinitionRepository(db)
        self.section_repo = FieldSectionRepository(db)

    def create(self, payload: FieldDefinitionCreate) -> FieldDefinition:
        if not self.section_repo.get(payload.section_id):
            raise NotFoundError("سکشن فیلد", payload.section_id)

        data = payload.model_dump(exclude={"options"})
        field = FieldDefinition(**data, is_system=False)
        try:
            self.repo.add(field)
            self.db.flush()

            for i, option_value in enumerate(payload.options or []):
                self.db.add(
                    FieldOption(
                        field_id=field.id,
                        value=option_value,
                        label=option_value,
                        sort_order=i,
                    )
                )

            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(f"فیلدی با اسلاگ «{payload.slug}» از قبل وجود دارد") from exc
        self.db.refresh(field)
        return field

    def get(self, field_id: uuid.UUID) -> FieldDefinition:
        field = self.repo.get(field_id)
        if not field:
            raise NotFoundError("فیلد پویا", field_id)
        return field

    def list(
        self, *, section_id: uuid.UUID | None = None, include_inactive: bool = True
    ) -> list[FieldDefinition]:
        query = self.db.query(FieldDefinition).order_by(FieldDefinition.sort_order.asc())
        if section_id is not None:
            query = query.filter_by(section_id=section_id)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.all()

    def update(self, field_id: uuid.UUID, payload: FieldDefinitionUpdate) -> FieldDefinition:
        field = self.get(field_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(field, key, value)
        self.db.commit()
        self.db.refresh(field)
        return field

    def set_active(self, field_id: uuid.UUID, is_active: bool) -> FieldDefinition:
        field = self.get(field_id)
        field.is_active = is_active
        self.db.commit()
        self.db.refresh(field)
        return field

    def reorder(self, payload: ReorderRequest) -> list[FieldDefinition]:
        ids = [item.id for item in payload.items]
        fields = self.db.query(FieldDefinition).filter(FieldDefinition.id.in_(ids)).all()
        found_ids = {f.id for f in fields}
        missing = set(ids) - found_ids
        if missing:
            raise NotFoundError("فیلد پویا", next(iter(missing)))

        order_map = {item.id: item.sort_order for item in payload.items}
        for field in fields:
            field.sort_order = order_map[field.id]
        self.db.commit()
        return self.list()

    def delete(self, field_id: uuid.UUID) -> None:
        field = self.get(field_id)
        if field.is_system:
            raise ValidationAppError("فیلدهای سیستمی قابل حذف نیستند؛ می‌توانید آن را غیرفعال کنید")
        if self.repo.has_historical_values(field_id):
            raise ValidationAppError(
                "این فیلد در معاملات قبلی مقدار ثبت‌شده دارد و برای حفظ یکپارچگی "
                "تاریخچه قابل حذف نیست؛ به‌جای حذف، آن را غیرفعال کنید"
            )
        self.repo.delete(field)
        self.db.commit()
