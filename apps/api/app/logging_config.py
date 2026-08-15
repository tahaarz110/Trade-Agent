"""Basic logging configuration for the API.

Kept intentionally simple in Phase 0: structured/JSON logging, request-id
correlation, and log shipping can be added in a later phase without changing
the call sites (`logging.getLogger(__name__)`).
"""
import logging
import sys

from app.config import settings

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configure_logging() -> None:
    level = logging.DEBUG if settings.app_env == "development" else logging.INFO

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers on reload
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(handler)

    # Quiet down noisy third-party loggers by default
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
