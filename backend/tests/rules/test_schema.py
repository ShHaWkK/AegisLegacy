from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain.language import Language
from app.domain.severity import Severity
from app.rules.schema import RuleDefinition

VALID_RULE = {
    "id": "PERL-CMD-001",
    "language": "perl",
    "severity": "critical",
    "title": "Potential command injection through system call",
    "patterns": [r"system\s*\("],
    "description": "Detects dangerous system command execution patterns.",
    "recommendation": "Validate and whitelist inputs.",
    "category": "command-injection",
}


def test_valid_rule_parses_correctly() -> None:
    rule = RuleDefinition.model_validate(VALID_RULE)

    assert rule.id == "PERL-CMD-001"
    assert rule.language is Language.PERL
    assert rule.severity is Severity.CRITICAL
    assert len(rule.patterns) == 1


@pytest.mark.parametrize(
    "bad_id",
    ["perl-cmd-001", "PERLCMD001", "PERL-CMD-1", "PERL_CMD_001", ""],
)
def test_invalid_id_format_is_rejected(bad_id: str) -> None:
    payload = {**VALID_RULE, "id": bad_id}
    with pytest.raises(ValidationError):
        RuleDefinition.model_validate(payload)


def test_empty_patterns_list_is_rejected() -> None:
    payload = {**VALID_RULE, "patterns": []}
    with pytest.raises(ValidationError):
        RuleDefinition.model_validate(payload)


def test_invalid_regex_pattern_is_rejected() -> None:
    payload = {**VALID_RULE, "patterns": ["("]}
    with pytest.raises(ValidationError):
        RuleDefinition.model_validate(payload)


def test_unknown_severity_is_rejected() -> None:
    payload = {**VALID_RULE, "severity": "apocalyptic"}
    with pytest.raises(ValidationError):
        RuleDefinition.model_validate(payload)


def test_unknown_language_is_rejected() -> None:
    payload = {**VALID_RULE, "language": "cobol"}
    with pytest.raises(ValidationError):
        RuleDefinition.model_validate(payload)


@pytest.mark.parametrize("field", ["title", "description", "recommendation", "category"])
def test_blank_text_fields_are_rejected(field: str) -> None:
    payload = {**VALID_RULE, field: "   "}
    with pytest.raises(ValidationError):
        RuleDefinition.model_validate(payload)


def test_compiled_patterns_match_expected_text() -> None:
    rule = RuleDefinition.model_validate(VALID_RULE)
    [compiled] = rule.compiled_patterns()

    assert compiled.search("system(\"ls\")")
    assert not compiled.search("systematic approach")
