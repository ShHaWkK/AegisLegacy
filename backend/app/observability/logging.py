"""Structured logging configuration.

Call `configure_logging` once at process startup (see app/main.py). After
that, `get_logger(__name__)` returns a structlog logger that emits JSON
lines by default — safe to pipe into any log aggregator without a custom
parser. Never log secrets, API keys, or full request bodies here.
"""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(*, level: str = "INFO", json_format: bool = True) -> None:
    logging.basicConfig(
        format="%(message)s", stream=sys.stdout, level=logging.getLevelName(level.upper())
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer() if json_format else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.typing.FilteringBoundLogger:
    return structlog.get_logger(name)  # type: ignore[no-any-return]
