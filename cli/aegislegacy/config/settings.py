"""Resolves CLI settings from explicit flags, environment, then defaults.

Precedence (highest first): an explicit --rules-dir flag, the
AEGIS_RULES_DIR environment variable, then the repo-relative rules/
directory (works out of the box for anyone running the CLI from a checkout
of this monorepo).
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    rules_dir: Path


def default_rules_dir() -> Path:
    """The rules/ directory at the root of this monorepo checkout."""
    return Path(__file__).resolve().parents[3] / "rules"


def load_settings(rules_dir: Path | None = None) -> Settings:
    if rules_dir is not None:
        resolved = rules_dir
    elif env_value := os.environ.get("AEGIS_RULES_DIR"):
        resolved = Path(env_value)
    else:
        resolved = default_rules_dir()
    return Settings(rules_dir=resolved)
