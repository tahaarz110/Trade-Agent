from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.checklist import ChecklistItem, ChecklistTemplate, TradeChecklistAnswer
from app.models.trade import Trade
from app.repositories.checklist import ChecklistItemRepository, ChecklistTemplateRepository
from app.repositories.trade import TradeRepository
from app.schemas.trade_checklist import (
    ChecklistAnswerInput,
    TradeChecklistItemRead,
    TradeChecklistRead,
    TradeChecklistSummary,
    TradeChecklistUpdate,
)
from app.services import NotFoundError, ValidationAppError


class TradeChecklistService:
    """پیاده‌سازی فاز ۵.۵ (اصلاحی): اختصاص قالب چک‌لیست به یک معامله،
    ثبت/به‌روزرسانی پاسخ آیتم‌ها، و محاسبه قطعی امتیاز رعایت چک‌لیست."""

    def __init__(self, db: Session):
        self.db = db
        self.trade_repo = TradeRepository(db)
        self.template_repo = ChecklistTemplateRepository(db)
        self.item_repo = ChecklistItemRepository(db)

    # --- خواندن / محاسبه --------------------------------------------------------
    def _build_read(self, trade: Trade) -> TradeChecklistRead:
        if trade.checklist_template_id is None:
            return TradeChecklistRead(trade_id=trade.id)

        template = self.template_repo.get(trade.checklist_template_id)
        if template is None:  # احتیاطی؛ عملاً با SET NULL نباید رخ دهد
            return TradeChecklistRead(trade_id=trade.id)

        all_items = (
            self.db.query(ChecklistItem)
            .filter_by(template_id=template.id)
            .order_by(ChecklistItem.sort_order.asc())
            .all()
        )
        answers_by_item = {
            a.checklist_item_id: a
            for a in self.db.query(TradeChecklistAnswer)
            .filter(
                TradeChecklistAnswer.trade_id == trade.id,
                TradeChecklistAnswer.checklist_item_id.in_([i.id for i in all_items]),
            )
            .all()
        }

        # طبق الزام فاز ۵.۵: آیتم‌های فعال + آیتم‌های غیرفعالی که پاسخ
        # تاریخی برای این معامله دارند (تا داده تاریخی هرگز مخفی نشود)
        visible_items = [item for item in all_items if item.is_active or item.id in answers_by_item]

        item_reads: list[TradeChecklistItemRead] = []
        for item in visible_items:
            answer = answers_by_item.get(item.id)
            item_reads.append(
                TradeChecklistItemRead(
                    id=item.id,
                    title=item.title,
                    description=item.description,
                    is_required=item.is_required,
                    sort_order=item.sort_order,
                    is_active=item.is_active,
                    checked=bool(answer.is_checked) if answer else False,
                    note=answer.note if answer else None,
                )
            )

        active_items = [i for i in item_reads if i.is_active]
        total_active = len(active_items)
        checked_active = sum(1 for i in active_items if i.checked)
        score_percent = round(checked_active / total_active * 100, 2) if total_active > 0 else None

        required_active = [i for i in active_items if i.is_required]
        required_checked = sum(1 for i in required_active if i.checked)
        missing_titles = [i.title for i in required_active if not i.checked]

        return TradeChecklistRead(
            trade_id=trade.id,
            checklist_template_id=template.id,
            checklist_template_title=template.name,
            items=item_reads,
            total_items=len(item_reads),
            checked_items=sum(1 for i in item_reads if i.checked),
            required_items=len(required_active),
            required_checked_items=required_checked,
            required_missing_items=missing_titles,
            score_percent=score_percent,
        )

    def get(self, trade_id: uuid.UUID) -> TradeChecklistRead:
        trade = self.trade_repo.get(trade_id)
        if not trade:
            raise NotFoundError("معامله", trade_id)
        return self._build_read(trade)

    def get_summary(self, trade: Trade) -> TradeChecklistSummary:
        """نسخه سبک جهت تعبیه در پاسخ جزئیات معامله (بدون بار اضافه بر
        endpoint اصلی). `trade` باید از قبل لود شده باشد."""
        if trade.checklist_template_id is None:
            return TradeChecklistSummary()
        full = self._build_read(trade)
        return TradeChecklistSummary(
            has_checklist=True,
            checklist_template_title=full.checklist_template_title,
            checklist_score_percent=full.score_percent,
            required_missing_count=len(full.required_missing_items),
        )

    # --- نوشتن ----------------------------------------------------------------
    def update(self, trade_id: uuid.UUID, payload: TradeChecklistUpdate) -> TradeChecklistRead:
        trade = self.trade_repo.get(trade_id)
        if not trade:
            raise NotFoundError("معامله", trade_id)

        if payload.checklist_template_id is not None:
            template = self.template_repo.get(payload.checklist_template_id)
            if not template:
                raise NotFoundError("قالب چک‌لیست", payload.checklist_template_id)
            # الزام اعتبارسنجی: فقط قالب فعال قابل اختصاص تازه است؛ اگر
            # همین قالب از قبل روی معامله بوده (حتی اگر بعداً غیرفعال
            # شده)، تغییری در تخصیص لازم نیست و مسدود نمی‌شود.
            if not template.is_active and trade.checklist_template_id != template.id:
                raise ValidationAppError(f"قالب «{template.name}» غیرفعال است و قابل اختصاص نیست")
            # طبق الزام «تغییر قالب باید پاسخ‌های قبلی را ایمن جایگزین
            # کند»: پاسخ‌های قدیمی حذف نمی‌شوند (چون به آیتم‌های قالب
            # قبلی متصل‌اند و تاریخچه باید بماند)، فقط اشاره‌گر معامله
            # به قالب جدید عوض می‌شود.
            trade.checklist_template_id = template.id
        else:
            trade.checklist_template_id = None

        if trade.checklist_template_id is not None and payload.answers:
            self._upsert_answers(trade_id, trade.checklist_template_id, payload.answers)

        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValidationAppError(
                "ثبت پاسخ‌های چک‌لیست به‌خاطر تعارض داده با خطا مواجه شد؛ دوباره تلاش کنید"
            ) from exc
        self.db.refresh(trade)
        return self._build_read(trade)

    def _upsert_answers(
        self,
        trade_id: uuid.UUID,
        template_id: uuid.UUID,
        answers: list[ChecklistAnswerInput],
    ) -> None:
        item_ids = [a.item_id for a in answers]
        items = {i.id: i for i in self.db.query(ChecklistItem).filter(ChecklistItem.id.in_(item_ids)).all()}

        existing_answers = {
            a.checklist_item_id: a
            for a in self.db.query(TradeChecklistAnswer)
            .filter(
                TradeChecklistAnswer.trade_id == trade_id,
                TradeChecklistAnswer.checklist_item_id.in_(item_ids),
            )
            .all()
        }

        # الزام «جلوگیری از پاسخ تکراری»: اگر یک آیتم چند بار در payload
        # آمده باشد، فقط آخرین مقدار اعمال و فقط یک ردیف نوشته می‌شود
        # (به‌جای تلاش برای insert چندباره که با unique constraint
        # پایگاه‌داده به خطای ۵۰۰ می‌انجامید).
        deduped: dict[uuid.UUID, ChecklistAnswerInput] = {a.item_id: a for a in answers}

        for item_id, answer in deduped.items():
            item = items.get(item_id)
            if item is None:
                raise NotFoundError("آیتم چک‌لیست", item_id)
            if item.template_id != template_id:
                raise ValidationAppError(f"آیتم «{item.title}» متعلق به قالب انتخاب‌شده نیست")

            existing = existing_answers.get(item_id)
            if existing is None and not item.is_active:
                # الزام اعتبارسنجی: فقط آیتم فعال در «ثبت جدید» قابل پاسخ‌دهی است
                raise ValidationAppError(f"آیتم «{item.title}» غیرفعال است و قابل پاسخ‌دهی جدید نیست")

            if existing:
                existing.is_checked = answer.checked
                existing.note = answer.note
            else:
                new_answer = TradeChecklistAnswer(
                    trade_id=trade_id,
                    checklist_item_id=item_id,
                    is_checked=answer.checked,
                    note=answer.note,
                )
                self.db.add(new_answer)
                existing_answers[item_id] = new_answer

    def assign_default(self, trade_id: uuid.UUID) -> TradeChecklistRead:
        trade = self.trade_repo.get(trade_id)
        if not trade:
            raise NotFoundError("معامله", trade_id)

        if trade.checklist_template_id is not None:
            # عملیات idempotent: معامله از قبل قالب دارد، تغییری اعمال نمی‌شود
            return self._build_read(trade)

        default_template: Optional[ChecklistTemplate] = (
            self.db.query(ChecklistTemplate).filter_by(is_default=True, is_active=True).first()
        )
        if default_template is None:
            raise NotFoundError("قالب چک‌لیست پیش‌فرض", "default")

        trade.checklist_template_id = default_template.id
        self.db.commit()
        self.db.refresh(trade)
        return self._build_read(trade)
