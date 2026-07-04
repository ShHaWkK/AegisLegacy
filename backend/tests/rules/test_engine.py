from __future__ import annotations

from pathlib import Path

import pytest

from app.domain.severity import Severity
from app.rules.engine import RuleEngine
from app.rules.schema import RuleDefinition

PERL_CMD_RULE = RuleDefinition.model_validate(
    {
        "id": "PERL-CMD-001",
        "language": "perl",
        "severity": "critical",
        "title": "Potential command injection",
        "patterns": [r"system\s*\("],
        "description": "desc",
        "recommendation": "rec",
        "category": "command-injection",
    }
)

PY_EVAL_RULE = RuleDefinition.model_validate(
    {
        "id": "PY-EVAL-001",
        "language": "python",
        "severity": "high",
        "title": "Use of eval",
        "patterns": [r"\beval\s*\("],
        "description": "desc",
        "recommendation": "rec",
        "category": "unsafe-eval",
    }
)

SECRET_RULE = RuleDefinition.model_validate(
    {
        "id": "SECRET-GENERIC-001",
        "language": "any",
        "severity": "critical",
        "title": "Hardcoded secret",
        "patterns": [r"(?i)password\s*=\s*[\"'][^\"']{4,}[\"']"],
        "description": "desc",
        "recommendation": "rec",
        "category": "hardcoded-secret",
    }
)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "legacy.pl").write_text(
        'print "hi";\nsystem("rm -rf $input");\n', encoding="utf-8"
    )
    (tmp_path / "script.py").write_text("x = 1\nresult = eval(user_input)\n", encoding="utf-8")
    (tmp_path / "config.conf").write_text('password = "hunter2super"\n', encoding="utf-8")
    (tmp_path / "notes.txt").write_text("nothing dangerous here\n", encoding="utf-8")
    (tmp_path / "image.bin").write_bytes(b"\xff\xd8\xff\xe0\x00\x10\xff\xfe")
    return tmp_path


def test_scan_file_matches_language_specific_rule(project: Path) -> None:
    engine = RuleEngine([PERL_CMD_RULE])

    findings = engine.scan_file(project / "legacy.pl", root=project)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "PERL-CMD-001"
    assert finding.severity is Severity.CRITICAL
    assert finding.file_path == "legacy.pl"
    assert finding.line_number == 2


def test_scan_file_does_not_apply_rule_to_wrong_language(project: Path) -> None:
    engine = RuleEngine([PERL_CMD_RULE])

    findings = engine.scan_file(project / "script.py", root=project)

    assert findings == []


def test_any_language_rule_applies_to_every_extension(project: Path) -> None:
    engine = RuleEngine([SECRET_RULE])

    findings = engine.scan_file(project / "config.conf", root=project)

    assert len(findings) == 1
    assert findings[0].rule_id == "SECRET-GENERIC-001"


def test_binary_files_are_skipped_without_error(project: Path) -> None:
    engine = RuleEngine([SECRET_RULE])

    findings = engine.scan_file(project / "image.bin", root=project)

    assert findings == []


def test_scan_tree_aggregates_findings_across_files(project: Path) -> None:
    engine = RuleEngine([PERL_CMD_RULE, PY_EVAL_RULE, SECRET_RULE])

    findings = engine.scan_tree(project)

    rule_ids = sorted(finding.rule_id for finding in findings)
    assert rule_ids == ["PERL-CMD-001", "PY-EVAL-001", "SECRET-GENERIC-001"]


def test_scan_tree_ignores_ignored_directories(tmp_path: Path) -> None:
    ignored = tmp_path / ".git"
    ignored.mkdir()
    (ignored / "hooks.py").write_text("eval(x)\n", encoding="utf-8")

    engine = RuleEngine([PY_EVAL_RULE])
    findings = engine.scan_tree(tmp_path)

    assert findings == []


def test_scan_tree_with_no_rules_returns_no_findings(project: Path) -> None:
    engine = RuleEngine([])

    assert engine.scan_tree(project) == []


def test_multiple_matches_on_same_line_are_all_reported(tmp_path: Path) -> None:
    (tmp_path / "double.pl").write_text('system("a"); system("b");\n', encoding="utf-8")
    engine = RuleEngine([PERL_CMD_RULE])

    findings = engine.scan_file(tmp_path / "double.pl", root=tmp_path)

    assert len(findings) == 2
    assert all(finding.line_number == 1 for finding in findings)
