from __future__ import annotations

from pathlib import Path

import pytest
from app.rules.paths import default_rules_dir

from aegislegacy.config.settings import load_settings


def test_default_rules_dir_points_at_repo_rules_directory() -> None:
    resolved = default_rules_dir()

    assert resolved.name == "rules"
    assert resolved.is_dir()


def test_load_settings_prefers_explicit_argument(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AEGIS_RULES_DIR", "/should/not/be/used")

    settings = load_settings(rules_dir=tmp_path)

    assert settings.rules_dir == tmp_path


def test_load_settings_falls_back_to_env_var(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AEGIS_RULES_DIR", str(tmp_path))

    settings = load_settings(rules_dir=None)

    assert settings.rules_dir == tmp_path


def test_load_settings_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AEGIS_RULES_DIR", raising=False)

    settings = load_settings(rules_dir=None)

    assert settings.rules_dir == default_rules_dir()
