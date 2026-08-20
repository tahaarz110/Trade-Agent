from __future__ import annotations

from app.models.checklist import ChecklistItem, ChecklistTemplate, TradeChecklistAnswer
from app.repositories.base import BaseRepository


class ChecklistTemplateRepository(BaseRepository[ChecklistTemplate]):
    model = ChecklistTemplate

    def has_historical_usage(self, template_id) -> bool:
        """بررسی می‌کند آیا این قالب توسط معامله‌ای انتخاب شده یا هریک
        از آیتم‌های آن پاسخ تاریخی دارد؛ در این صورت حذف قالب (که با
        CASCADE آیتم‌ها و به‌تبع پاسخ‌ها را نابود می‌کند) مسدود می‌شود."""
        from app.models.trade import Trade

        used_by_trade = (
            self.db.query(Trade.id).filter_by(checklist_template_id=template_id).limit(1).first()
        )
        if used_by_trade is not None:
            return True

        item_ids = [
            i.id for i in self.db.query(ChecklistItem.id).filter_by(template_id=template_id).all()
        ]
        if not item_ids:
            return False
        return (
            self.db.query(TradeChecklistAnswer.id)
            .filter(TradeChecklistAnswer.checklist_item_id.in_(item_ids))
            .limit(1)
            .first()
            is not None
        )


class ChecklistItemRepository(BaseRepository[ChecklistItem]):
    model = ChecklistItem

    def has_historical_answers(self, item_id) -> bool:
        return (
            self.db.query(TradeChecklistAnswer.id)
            .filter_by(checklist_item_id=item_id)
            .limit(1)
            .first()
            is not None
        )
