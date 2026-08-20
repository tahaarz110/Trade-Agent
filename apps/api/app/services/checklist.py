from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.checklist import ChecklistItem, ChecklistTemplate
from app.repositories.checklist import ChecklistItemRepository, ChecklistTemplateRepository
from app.schemas.checklist import (
    ChecklistItemCreate,
    ChecklistItemUpdate,
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
)
from app.schemas.common import ReorderRequest
from app.services import NotFoundError, ValidationAppError


class ChecklistTemplateService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChecklistTemplateRepository(db)

    def create(self, payload: ChecklistTemplateCreate) -> ChecklistTemplate:
        template = ChecklistTemplate(**payload.model_dump())
        self.repo.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get(self, template_id: uuid.UUID) -> ChecklistTemplate:
        template = self.repo.get(template_id)
        if not template:
            raise NotFoundError("قالب چک‌لیست", template_id)
        return template

    def list(self, *, include_inactive: bool = True) -> list[ChecklistTemplate]:
        query = self.db.query(ChecklistTemplate).order_by(ChecklistTemplate.created_at.asc())
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.all()

    def update(self, template_id: uuid.UUID, payload: ChecklistTemplateUpdate) -> ChecklistTemplate:
        template = self.get(template_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(template, key, value)
        self.db.commit()
        self.db.refresh(template)
        return template

    def set_active(self, template_id: uuid.UUID, is_active: bool) -> ChecklistTemplate:
        template = self.get(template_id)
        template.is_active = is_active
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete(self, template_id: uuid.UUID) -> None:
        template = self.get(template_id)
        if self.repo.has_historical_usage(template_id):
            raise ValidationAppError(
                "این قالب توسط معامله‌ای استفاده شده یا آیتم‌های آن پاسخ تاریخی دارند؛ "
                "برای حفظ یکپارچگی تاریخچه قابل حذف نیست؛ به‌جای حذف، آن را غیرفعال کنید"
            )
        self.repo.delete(template)
        self.db.commit()


class ChecklistItemService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChecklistItemRepository(db)
        self.template_repo = ChecklistTemplateRepository(db)

    def create(self, payload: ChecklistItemCreate) -> ChecklistItem:
        if not self.template_repo.get(payload.template_id):
            raise NotFoundError("قالب چک‌لیست", payload.template_id)
        item = ChecklistItem(**payload.model_dump())
        self.repo.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, item_id: uuid.UUID) -> ChecklistItem:
        item = self.repo.get(item_id)
        if not item:
            raise NotFoundError("آیتم چک‌لیست", item_id)
        return item

    def list_for_template(self, template_id: uuid.UUID) -> list[ChecklistItem]:
        return (
            self.db.query(ChecklistItem)
            .filter_by(template_id=template_id)
            .order_by(ChecklistItem.sort_order.asc())
            .all()
        )

    def update(self, item_id: uuid.UUID, payload: ChecklistItemUpdate) -> ChecklistItem:
        item = self.get(item_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def set_active(self, item_id: uuid.UUID, is_active: bool) -> ChecklistItem:
        item = self.get(item_id)
        item.is_active = is_active
        self.db.commit()
        self.db.refresh(item)
        return item

    def reorder(self, template_id: uuid.UUID, payload: ReorderRequest) -> list[ChecklistItem]:
        ids = [i.id for i in payload.items]
        items = (
            self.db.query(ChecklistItem)
            .filter(ChecklistItem.id.in_(ids), ChecklistItem.template_id == template_id)
            .all()
        )
        found_ids = {i.id for i in items}
        missing = set(ids) - found_ids
        if missing:
            raise NotFoundError("آیتم چک‌لیست", next(iter(missing)))

        order_map = {i.id: i.sort_order for i in payload.items}
        for item in items:
            item.sort_order = order_map[item.id]
        self.db.commit()
        return self.list_for_template(template_id)

    def delete(self, item_id: uuid.UUID) -> None:
        item = self.get(item_id)
        if self.repo.has_historical_answers(item_id):
            raise ValidationAppError(
                "این آیتم در پاسخ‌های چک‌لیست معاملات قبلی استفاده شده و برای حفظ "
                "یکپارچگی تاریخچه قابل حذف نیست"
            )
        self.repo.delete(item)
        self.db.commit()
