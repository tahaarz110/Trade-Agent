"""پیکربندی مشترک تست‌ها.

از یک دیتابیس PostgreSQL جداگانه (`trade_agent_test`) استفاده می‌شود تا
داده‌های توسعه/تولید دست‌نخورده بماند. جدول‌ها یک‌بار در ابتدای session
ساخته و در پایان حذف می‌شوند؛ بین هر تست همه جدول‌ها TRUNCATE می‌شوند
تا تست‌ها کاملاً از هم مستقل باشند.
"""
import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://trade_agent:trade_agent@localhost:5432/trade_agent_test",
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401  ثبت مدل‌ها روی Base.metadata
from app.config import settings
from app.database import Base, get_db
from app.main import app as fastapi_app

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    yield
    with engine.begin() as conn:
        table_names = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
        conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(tmp_path, monkeypatch):
    # مسیرهای ذخیره‌سازی پیوست را برای هر تست به یک پوشه موقت جدا هدایت می‌کنیم
    monkeypatch.setattr(settings, "attachment_dir", str(tmp_path / "attachments"))

    def _override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def account_payload():
    return {
        "name": "حساب دمو تست",
        "account_type": "demo",
        "currency": "USD",
        "initial_balance": 10000,
    }


@pytest.fixture
def symbol_payload():
    return {
        "name": "EURUSD",
        "display_name": "یورو/دلار",
        "asset_class": "forex",
    }


@pytest.fixture
def account_id(client, account_payload):
    resp = client.post("/accounts", json=account_payload)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture
def symbol_id(client, symbol_payload):
    resp = client.post("/symbols", json=symbol_payload)
    assert resp.status_code == 201
    return resp.json()["id"]
