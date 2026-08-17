from __future__ import annotations

from app.models.checklist import ChecklistItem, ChecklistTemplate, TradeChecklistAnswer
from app.repositories.base import BaseRepository


class ChecklistTemplateRepository(BaseRepository[ChecklistTemplate]):
    model = ChecklistTemplate


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
