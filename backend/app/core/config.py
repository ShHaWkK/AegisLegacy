"""Centralized application settings, sourced from environment variables.

All settings are prefixed with AEGIS_ (see .env.example at the repo root).
This is the single place the rest of the codebase should read configuration
from — no module should call os.environ directly.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_rules_dir() -> Path:
    """The rules/ directory at the root of this monorepo checkout."""
    return Path(__file__).resolve().parents[3] / "rules"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AEGIS_", env_file=".env", extra="ignore")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: str = "changeme-local-dev-key"

    database_url: str = "sqlite:///./aegislegacy.db"

    rules_dir: Path = Path()  # resolved to _default_rules_dir() in model_post_init

    reports_dir: Path = Path("./reports")

    log_level: str = "INFO"
    log_format: str = "json"

    def model_post_init(self, __context: Any) -> None:
        if self.rules_dir == Path():
            self.rules_dir = _default_rules_dir()


@lru_cache
def get_settings() -> Settings:
    """Cached Settings instance; call get_settings.cache_clear() in tests."""
    return Settings()
