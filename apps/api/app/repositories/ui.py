from __future__ import annotations

from app.models.ui import ThemeSetting, UITab
from app.repositories.base import BaseRepository


class ThemeSettingRepository(BaseRepository[ThemeSetting]):
    model = ThemeSetting

    def get_by_key(self, key: str) -> ThemeSetting | None:
        return self.db.query(ThemeSetting).filter_by(key=key).first()


class UITabRepository(BaseRepository[UITab]):
    model = UITab

    def get_by_key(self, key: str) -> UITab | None:
        return self.db.query(UITab).filter_by(key=key).first()
