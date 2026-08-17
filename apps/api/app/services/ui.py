from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.ui import ThemeSetting, UITab
from app.repositories.ui import ThemeSettingRepository, UITabRepository
from app.schemas.common import ReorderRequest
from app.schemas.ui import ThemeSettingUpdate, UITabCreate, UITabUpdate
from app.services import ConflictError, NotFoundError
from sqlalchemy.exc import IntegrityError

DEFAULT_THEME_KEY = "default"


class ThemeSettingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ThemeSettingRepository(db)

    def get_or_create_default(self) -> ThemeSetting:
        """تنظیمات تم به‌صورت یک رکورد singleton با key='default' نگه‌داری
        می‌شود؛ در صورت نبودن (مثلاً پیش از اجرای seed)، همینجا ساخته
        می‌شود تا کلاینت همیشه یک مقدار معتبر دریافت کند."""
        theme = self.repo.get_by_key(DEFAULT_THEME_KEY)
        if theme is None:
            theme = ThemeSetting(key=DEFAULT_THEME_KEY, theme_name="light")
            self.repo.add(theme)
            self.db.commit()
            self.db.refresh(theme)
        return theme

    def update(self, payload: ThemeSettingUpdate) -> ThemeSetting:
        theme = self.get_or_create_default()
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(theme, key, value)
        self.db.commit()
        self.db.refresh(theme)
        return theme


class UITabService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UITabRepository(db)

    def create(self, payload: UITabCreate) -> UITab:
        tab = UITab(**payload.model_dump())
        try:
            self.repo.add(tab)
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(f"تبی با کلید «{payload.key}» از قبل وجود دارد") from exc
        self.db.refresh(tab)
        return tab

    def get(self, tab_id: uuid.UUID) -> UITab:
        tab = self.repo.get(tab_id)
        if not tab:
            raise NotFoundError("تب رابط کاربری", tab_id)
        return tab

    def list(self) -> list[UITab]:
        return self.db.query(UITab).order_by(UITab.sort_order.asc()).all()

    def update(self, tab_id: uuid.UUID, payload: UITabUpdate) -> UITab:
        tab = self.get(tab_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(tab, key, value)
        self.db.commit()
        self.db.refresh(tab)
        return tab

    def set_visible(self, tab_id: uuid.UUID, is_visible: bool) -> UITab:
        tab = self.get(tab_id)
        tab.is_visible = is_visible
        self.db.commit()
        self.db.refresh(tab)
        return tab

    def reorder(self, payload: ReorderRequest) -> list[UITab]:
        ids = [item.id for item in payload.items]
        tabs = self.db.query(UITab).filter(UITab.id.in_(ids)).all()
        found_ids = {t.id for t in tabs}
        missing = set(ids) - found_ids
        if missing:
            raise NotFoundError("تب رابط کاربری", next(iter(missing)))

        order_map = {item.id: item.sort_order for item in payload.items}
        for tab in tabs:
            tab.sort_order = order_map[tab.id]
        self.db.commit()
        return self.list()

    def delete(self, tab_id: uuid.UUID) -> None:
        tab = self.get(tab_id)
        self.repo.delete(tab)
        self.db.commit()
