"""Application configuration loaded from environment variables.

All settings are documented in `apps/api/.env.example`. This module is the
single source of truth for configuration across the API; every other module
must import `settings` from here instead of reading `os.environ` directly.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---------------------------------------------------------------
    app_name: str = "Professional ICT Trading Journal API"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # --- Database ------------------------------------------------------------
    database_url: str = (
        "postgresql+psycopg://trade_agent:trade_agent@localhost:5432/trade_agent"
    )

    # --- Storage paths ---------------------------------------------------------
    attachment_dir: str = "../../storage/attachments"
    backup_dir: str = "../../storage/backups"
    parquet_dir: str = "../../storage/analytics/parquet"

    # --- Feature flags ------------------------------------------------------
    low_resource_mode: bool = True
    ai_narrator_enabled: bool = False
    analytics_schedule: str = "daily"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_storage_dirs(self) -> None:
        """Create storage directories on startup if they do not exist yet."""
        for path in (self.attachment_dir, self.backup_dir, self.parquet_dir):
            Path(path).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
