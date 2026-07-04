"""Pydantic schema for YAML rule definitions, with regex validation.

A rule file looks like:

    id: PERL-CMD-001
    language: perl
    severity: critical
    title: Potential command injection through system call
    patterns:
      - "system\\s*\\("
      - "`[^`]+`"
    description: Detects dangerous system command execution patterns.
    recommendation: Validate and whitelist inputs. Avoid shell interpolation.
    category: command-injection
"""

from __future__ import annotations

import re
from re import Pattern

from pydantic import BaseModel, ConfigDict, field_validator

from app.domain.language import Language
from app.domain.severity import Severity

_ID_PATTERN: Pattern[str] = re.compile(r"^[A-Z]+-[A-Z0-9]+-\d{3}$")


class RuleSchemaError(ValueError):
    """Raised when a rule file does not satisfy the rule schema."""


class RuleDefinition(BaseModel):
    """A single validated detection rule, as loaded from YAML."""

    model_config = ConfigDict(frozen=True)

    id: str
    language: Language
    severity: Severity
    title: str
    patterns: list[str]
    description: str
    recommendation: str
    category: str

    @field_validator("id")
    @classmethod
    def _validate_id(cls, value: str) -> str:
        if not _ID_PATTERN.match(value):
            raise RuleSchemaError(
                f"Rule id {value!r} must match <NAMESPACE>-<TOPIC>-<NNN>, "
                "e.g. PERL-CMD-001"
            )
        return value

    @field_validator("patterns")
    @classmethod
    def _validate_patterns(cls, value: list[str]) -> list[str]:
        if not value:
            raise RuleSchemaError("A rule must declare at least one pattern")
        for pattern in value:
            try:
                re.compile(pattern)
            except re.error as exc:
                raise RuleSchemaError(f"Invalid regex pattern {pattern!r}: {exc}") from exc
        return value

    @field_validator("title", "description", "recommendation", "category")
    @classmethod
    def _validate_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise RuleSchemaError("Field must not be empty")
        return value

    def compiled_patterns(self) -> list[Pattern[str]]:
        return [re.compile(pattern) for pattern in self.patterns]
