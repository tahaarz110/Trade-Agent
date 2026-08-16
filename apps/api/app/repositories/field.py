from typing import Optional

from app.models.field import FieldDefinition, FieldOption, FieldSection, TradeFieldValue
from app.repositories.base import BaseRepository


class FieldSectionRepository(BaseRepository[FieldSection]):
    model = FieldSection

    def get_by_key(self, key: str) -> Optional[FieldSection]:
        return self.db.query(FieldSection).filter_by(key=key).first()

    def has_fields_with_historical_values(self, section_id) -> bool:
        field_ids = [
            f.id for f in self.db.query(FieldDefinition.id).filter_by(section_id=section_id).all()
        ]
        if not field_ids:
            return False
        return (
            self.db.query(TradeFieldValue.id)
            .filter(TradeFieldValue.field_id.in_(field_ids))
            .limit(1)
            .first()
            is not None
        )


class FieldDefinitionRepository(BaseRepository[FieldDefinition]):
    model = FieldDefinition

    def get_by_slug(self, slug: str) -> Optional[FieldDefinition]:
        """فیلد را با اسلاگ برمی‌گرداند، صرف‌نظر از فعال/غیرفعال بودن؛
        تصمیم رد کردن مقدار برای فیلد غیرفعال بر عهده لایه سرویس است تا
        پیام خطای دقیق‌تری (نه صرفاً «یافت نشد») بدهد."""
        return self.db.query(FieldDefinition).filter_by(slug=slug).first()

    def has_historical_values(self, field_id) -> bool:
        return (
            self.db.query(TradeFieldValue.id).filter_by(field_id=field_id).limit(1).first()
            is not None
        )


class FieldOptionRepository(BaseRepository[FieldOption]):
    model = FieldOption

    def is_option_value_used(self, field_id, option_value: str) -> bool:
        """بررسی می‌کند آیا مقدار این گزینه در هیچ معامله‌ای ثبت شده یا نه
        (برای متن تکی value_text یا برای چندانتخابی درون value_json)."""
        rows = (
            self.db.query(TradeFieldValue.value_text, TradeFieldValue.value_json)
            .filter_by(field_id=field_id)
            .all()
        )
        for value_text, value_json in rows:
            if value_text == option_value:
                return True
            if isinstance(value_json, list) and option_value in value_json:
                return True
        return False
