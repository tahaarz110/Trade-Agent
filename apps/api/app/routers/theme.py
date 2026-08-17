from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ui import ThemeSettingRead, ThemeSettingUpdate
from app.services.ui import ThemeSettingService

router = APIRouter(prefix="/theme-settings", tags=["settings"])


@router.get("", response_model=ThemeSettingRead)
def get_theme(db: Session = Depends(get_db)) -> ThemeSettingRead:
    theme = ThemeSettingService(db).get_or_create_default()
    return ThemeSettingRead.model_validate(theme)


@router.patch("", response_model=ThemeSettingRead)
def update_theme(payload: ThemeSettingUpdate, db: Session = Depends(get_db)) -> ThemeSettingRead:
    theme = ThemeSettingService(db).update(payload)
    return ThemeSettingRead.model_validate(theme)
