"""SQLAlchemy 2.x engine and session management.

Phase 0 only wires the engine/session so the /health endpoint can verify
DB connectivity and future phases can `from app.database import get_db,
Base` without further plumbing. No ORM models are defined yet.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Base class for all future ORM models (accounts, trades, etc.)."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
