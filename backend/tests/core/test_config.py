from __future__ import annotations

import pytest

from app.core.config import Settings, get_settings


def test_defaults_are_sane() -> None:
    settings = Settings()

    assert settings.api_port == 8000
    assert settings.database_url.startswith("sqlite:")
    assert settings.rules_dir.name == "rules"
    assert settings.rules_dir.is_dir()


def test_settings_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AEGIS_API_PORT", "9001")
    monkeypatch.setenv("AEGIS_API_KEY", "custom-key")

    settings = Settings()

    assert settings.api_port == 9001
    assert settings.api_key == "custom-key"


def test_get_settings_is_cached() -> None:
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second
    get_settings.cache_clear()
