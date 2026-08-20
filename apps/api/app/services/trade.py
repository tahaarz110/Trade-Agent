from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import FieldType
from app.models.field import FieldDefinition
from app.models.trade import Trade
from app.models.field import TradeFieldValue
from app.repositories.account import AccountRepository
from app.repositories.field import FieldDefinitionRepository
from app.repositories.symbol import SymbolRepository
from app.repositories.trade import TradeFilters, TradeRepository
from app.schemas.trade import TradeCreate, TradeDetailRead, TradeFieldValueRead, TradeUpdate
from app.services import ConflictError, NotFoundError, ValidationAppError

# نگاشت نوع فیلد پویا به ستون تایپ‌شده در trade_field_values
_TEXT_TYPES = {
    FieldType.SHORT_TEXT,
    FieldType.LONG_TEXT,
    FieldType.URL,
    FieldType.SYMBOL,
    FieldType.FILE,
    FieldType.TIME,
}
_NUMBER_TYPES = {FieldType.NUMBER, FieldType.PRICE, FieldType.PERCENT}
_SINGLE_CHOICE_TYPES = {FieldType.SINGLE_SELECT, FieldType.RADIO}
_MULTI_CHOICE_TYPES = {FieldType.MULTI_SELECT, FieldType.CHECKBOX}
_BOOLEAN_TRUE_STRINGS = {"true", "1", "yes", "on", "بله", "درست"}
_BOOLEAN_FALSE_STRINGS = {"false", "0", "no", "off", "خیر", "نادرست"}


class TradeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TradeRepository(db)
        self.account_repo = AccountRepository(db)
        self.symbol_repo = SymbolRepository(db)
        self.field_repo = FieldDefinitionRepository(db)

    # --- کمکی‌های اعتبارسنجی مقدار فیلد پویا -----------------------------------
    def _coerce_boolean(self, raw_value: Any, field_title: str) -> bool:
        if isinstance(raw_value, bool):
            return raw_value
        if isinstance(raw_value, str):
            low = raw_value.strip().lower()
            if low in _BOOLEAN_TRUE_STRINGS:
                return True
            if low in _BOOLEAN_FALSE_STRINGS:
                return False
        raise ValidationAppError(f"مقدار فیلد «{field_title}» باید بولی (true/false) باشد")

    def _coerce_number(self, raw_value: Any, field_title: str) -> Decimal:
        try:
            return Decimal(str(raw_value))
        except (InvalidOperation, ValueError) as exc:
            raise ValidationAppError(f"مقدار فیلد «{field_title}» باید عددی باشد") from exc

    def _coerce_date(self, raw_value: Any, field_title: str) -> date:
        if isinstance(raw_value, date):
            return raw_value
        try:
            return date.fromisoformat(str(raw_value))
        except ValueError as exc:
            raise ValidationAppError(
                f"مقدار فیلد «{field_title}» باید تاریخ معتبر (YYYY-MM-DD) باشد"
            ) from exc

    def _coerce_datetime(self, raw_value: Any, field_title: str) -> datetime:
        if isinstance(raw_value, datetime):
            return raw_value
        try:
            return datetime.fromisoformat(str(raw_value))
        except ValueError as exc:
            raise ValidationAppError(
                f"مقدار فیلد «{field_title}» باید تاریخ‌زمان معتبر (ISO 8601) باشد"
            ) from exc

    def _validate_choice(
        self, field: FieldDefinition, raw_value: Any, *, multi: bool
    ) -> Any:
        allowed = {opt.value for opt in field.options if opt.is_active}
        if not multi:
            if str(raw_value) not in allowed:
                raise ValidationAppError(
                    f"مقدار «{raw_value}» برای فیلد «{field.title}» در گزینه‌های مجاز نیست"
                )
            return str(raw_value)

        values = raw_value if isinstance(raw_value, list) else [raw_value]
        invalid = [v for v in values if str(v) not in allowed]
        if invalid:
            raise ValidationAppError(
                f"مقادیر {invalid} برای فیلد «{field.title}» در گزینه‌های مجاز نیستند"
            )
        return [str(v) for v in values]

    # --- کمکی‌ها -------------------------------------------------------------
    def _apply_custom_field(self, trade_id: uuid.UUID, slug: str, raw_value: Any) -> None:
        field: Optional[FieldDefinition] = self.field_repo.get_by_slug(slug)
        if field is None:
            raise ValidationAppError(f"فیلد پویا با شناسه «{slug}» یافت نشد")
        if not field.is_active:
            raise ValidationAppError(f"فیلد «{field.title}» غیرفعال است و قابل مقداردهی نیست")

        existing = (
            self.db.query(TradeFieldValue)
            .filter_by(trade_id=trade_id, field_id=field.id)
            .first()
        )
        value_obj = existing or TradeFieldValue(trade_id=trade_id, field_id=field.id)

        # پاک‌سازی مقادیر قبلی همه ستون‌ها
        value_obj.value_text = None
        value_obj.value_number = None
        value_obj.value_boolean = None
        value_obj.value_date = None
        value_obj.value_datetime = None
        value_obj.value_json = None

        if raw_value is None:
            if field.is_required:
                raise ValidationAppError(f"فیلد «{field.title}» الزامی است و نمی‌تواند خالی باشد")
            self.db.add(value_obj)
            return

        if field.field_type in _NUMBER_TYPES:
            value_obj.value_number = self._coerce_number(raw_value, field.title)
        elif field.field_type == FieldType.BOOLEAN:
            value_obj.value_boolean = self._coerce_boolean(raw_value, field.title)
        elif field.field_type == FieldType.DATE:
            value_obj.value_date = self._coerce_date(raw_value, field.title)
        elif field.field_type == FieldType.DATETIME:
            value_obj.value_datetime = self._coerce_datetime(raw_value, field.title)
        elif field.field_type in _MULTI_CHOICE_TYPES:
            value_obj.value_json = self._validate_choice(field, raw_value, multi=True)
        elif field.field_type in _SINGLE_CHOICE_TYPES:
            value_obj.value_text = self._validate_choice(field, raw_value, multi=False)
        elif field.field_type in _TEXT_TYPES:
            value_obj.value_text = str(raw_value)
        else:
            value_obj.value_json = raw_value

        self.db.add(value_obj)

    def _sync_custom_fields(self, trade_id: uuid.UUID, custom_fields: dict[str, Any]) -> None:
        for slug, raw_value in custom_fields.items():
            self._apply_custom_field(trade_id, slug, raw_value)

    # --- عملیات CRUD -----------------------------------------------------------
    def create(self, payload: TradeCreate) -> Trade:
        if not self.account_repo.get(payload.account_id):
            raise NotFoundError("حساب", payload.account_id)
        if not self.symbol_repo.get(payload.symbol_id):
            raise NotFoundError("نماد", payload.symbol_id)

        data = payload.model_dump(exclude={"custom_fields"})
        trade = Trade(**data)

        if trade.exit_time and trade.entry_time:
            trade.duration_minutes = int((trade.exit_time - trade.entry_time).total_seconds() // 60)

        try:
            self.repo.add(trade)
            self.db.flush()

            if payload.custom_fields:
                self._sync_custom_fields(trade.id, payload.custom_fields)

            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(
                "معامله‌ای با همین import_hash برای این حساب قبلاً ثبت شده است"
            ) from exc
        self.db.refresh(trade)
        return trade

    def get(self, trade_id: uuid.UUID) -> Trade:
        trade = self.repo.get(trade_id)
        if not trade:
            raise NotFoundError("معامله", trade_id)
        return trade

    def get_detail(self, trade_id: uuid.UUID) -> TradeDetailRead:
        trade = self.get(trade_id)
        values = (
            self.db.query(TradeFieldValue)
            .filter_by(trade_id=trade_id)
            .join(FieldDefinition)
            .all()
        )
        custom_fields = []
        for v in values:
            raw = (
                v.value_text
                if v.value_text is not None
                else v.value_number
                if v.value_number is not None
                else v.value_boolean
                if v.value_boolean is not None
                else v.value_date
                if v.value_date is not None
                else v.value_datetime
                if v.value_datetime is not None
                else v.value_json
            )
            custom_fields.append(
                TradeFieldValueRead(
                    field_slug=v.field.slug,
                    field_title=v.field.title,
                    field_type=v.field.field_type.value
                    if hasattr(v.field.field_type, "value")
                    else str(v.field.field_type),
                    value=raw,
                )
            )

        # فاز ۵.۵: خلاصه سبک چک‌لیست بدون سنگین کردن این endpoint
        from app.services.trade_checklist import TradeChecklistService

        checklist_summary = TradeChecklistService(self.db).get_summary(trade)

        return TradeDetailRead.model_validate(trade, from_attributes=True).model_copy(
            update={
                "custom_fields": custom_fields,
                "has_checklist": checklist_summary.has_checklist,
                "checklist_template_title": checklist_summary.checklist_template_title,
                "checklist_score_percent": checklist_summary.checklist_score_percent,
                "required_missing_count": checklist_summary.required_missing_count,
            }
        )

    def list(
        self, *, filters: TradeFilters, offset: int, limit: int
    ) -> tuple[list[Trade], int]:
        return self.repo.list_filtered(filters=filters, offset=offset, limit=limit)

    def update(self, trade_id: uuid.UUID, payload: TradeUpdate) -> Trade:
        trade = self.get(trade_id)
        data = payload.model_dump(exclude_unset=True, exclude={"custom_fields"})
        for key, value in data.items():
            setattr(trade, key, value)

        if trade.exit_time and trade.entry_time:
            trade.duration_minutes = int((trade.exit_time - trade.entry_time).total_seconds() // 60)

        if payload.custom_fields:
            self._sync_custom_fields(trade.id, payload.custom_fields)

        self.db.commit()
        self.db.refresh(trade)
        return trade

    def delete(self, trade_id: uuid.UUID) -> None:
        trade = self.get(trade_id)
        self.repo.delete(trade)
        self.db.commit()
