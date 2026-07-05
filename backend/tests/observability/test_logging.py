from __future__ import annotations

import json

import pytest
import structlog

from app.observability.logging import configure_logging, get_logger


@pytest.fixture(autouse=True)
def _reset_structlog() -> None:
    yield
    structlog.reset_defaults()


def test_configure_logging_json_emits_parseable_json_line(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(level="INFO", json_format=True)
    logger = get_logger("test.logger")

    logger.info("hello", extra_field="value")

    captured = capsys.readouterr()
    line = captured.out.strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload["event"] == "hello"
    assert payload["extra_field"] == "value"
    assert payload["level"] == "info"


def test_configure_logging_console_does_not_emit_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(level="INFO", json_format=False)
    logger = get_logger("test.logger")

    logger.info("hello console")

    captured = capsys.readouterr()
    line = captured.out.strip().splitlines()[-1]
    with pytest.raises(json.JSONDecodeError):
        json.loads(line)
    assert "hello console" in line


def test_configure_logging_filters_below_configured_level(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(level="WARNING", json_format=True)
    logger = get_logger("test.logger")

    logger.info("should be filtered out")
    logger.warning("should appear")

    captured = capsys.readouterr()
    assert "should be filtered out" not in captured.out
    assert "should appear" in captured.out
