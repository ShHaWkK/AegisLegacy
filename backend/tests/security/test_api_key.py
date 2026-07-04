from __future__ import annotations

from app.security.api_key import verify_api_key


def test_correct_key_is_accepted() -> None:
    assert verify_api_key("secret123", "secret123") is True


def test_wrong_key_is_rejected() -> None:
    assert verify_api_key("wrong", "secret123") is False


def test_missing_key_is_rejected() -> None:
    assert verify_api_key(None, "secret123") is False


def test_empty_key_is_rejected() -> None:
    assert verify_api_key("", "secret123") is False
