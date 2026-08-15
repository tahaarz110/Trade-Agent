import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    """Liveness/readiness probe.

    Always returns HTTP 200 with `status: ok` once the API process is up,
    but also reports database connectivity so operators/CI can distinguish
    "API is up" from "API + DB stack is fully up" during `docker compose up`.
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - health check must never crash
        logger.warning("Database health check failed: %s", exc)
        db_status = "unavailable"

    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "time": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "low_resource_mode": settings.low_resource_mode,
        "ai_narrator_enabled": settings.ai_narrator_enabled,
    }
