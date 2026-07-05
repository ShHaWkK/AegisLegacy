"""Configuration centralisée, lue depuis les variables d'environnement.

Tout est préfixé par AEGIS_ (voir .env.example à la racine du repo). C'est
le seul endroit du code qui doit lire la config — aucun autre module ne
doit appeler os.environ directement.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.rules.paths import default_rules_dir


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AEGIS_", env_file=".env", extra="ignore")

    api_host: str = "0.0.0.0"  # noqa: S104 - doit être joignable hors localhost par défaut
    api_port: int = 8000
    api_key: str = "changeme-local-dev-key"

    database_url: str = "sqlite:///./aegislegacy.db"

    rules_dir: Path = Field(default_factory=default_rules_dir)

    reports_dir: Path = Path("./reports")

    log_level: str = "INFO"
    log_format: str = "json"


@lru_cache
def get_settings() -> Settings:
    """Instance Settings mise en cache ; appeler get_settings.cache_clear() dans les tests."""
    return Settings()
