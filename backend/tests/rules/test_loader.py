from __future__ import annotations

from pathlib import Path

import pytest

from app.rules.loader import RuleLoadError, load_rule_file, load_rules_from_directory

VALID_YAML = """
id: PY-EVAL-001
language: python
severity: high
title: Use of eval()
patterns:
  - "\\\\beval\\\\s*\\\\("
description: Detects eval() usage.
recommendation: Avoid eval().
category: unsafe-eval
"""


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_load_valid_rule_file(tmp_path: Path) -> None:
    rule_file = _write(tmp_path / "eval.yaml", VALID_YAML)

    rule = load_rule_file(rule_file)

    assert rule.id == "PY-EVAL-001"


def test_load_rule_file_with_malformed_yaml_raises(tmp_path: Path) -> None:
    rule_file = _write(tmp_path / "broken.yaml", "id: [unclosed")

    with pytest.raises(RuleLoadError):
        load_rule_file(rule_file)


def test_load_rule_file_that_is_not_a_mapping_raises(tmp_path: Path) -> None:
    rule_file = _write(tmp_path / "list.yaml", "- one\n- two\n")

    with pytest.raises(RuleLoadError):
        load_rule_file(rule_file)


def test_load_rule_file_failing_schema_validation_raises(tmp_path: Path) -> None:
    rule_file = _write(tmp_path / "bad.yaml", "id: PY-EVAL-001\nlanguage: python\n")

    with pytest.raises(RuleLoadError):
        load_rule_file(rule_file)


def test_load_rules_from_directory_recurses_and_sorts(tmp_path: Path) -> None:
    sub_dir = tmp_path / "python"
    sub_dir.mkdir()
    _write(sub_dir / "eval.yaml", VALID_YAML)
    _write(
        tmp_path / "cmd.yml",
        VALID_YAML.replace("PY-EVAL-001", "PERL-CMD-001").replace("python", "perl"),
    )

    rules = load_rules_from_directory(tmp_path)

    assert {rule.id for rule in rules} == {"PY-EVAL-001", "PERL-CMD-001"}


def test_load_rules_from_directory_rejects_duplicate_ids(tmp_path: Path) -> None:
    _write(tmp_path / "one.yaml", VALID_YAML)
    _write(tmp_path / "two.yaml", VALID_YAML)

    with pytest.raises(RuleLoadError, match="duplicate rule id"):
        load_rules_from_directory(tmp_path)


def test_load_rules_from_empty_directory_returns_empty_list(tmp_path: Path) -> None:
    assert load_rules_from_directory(tmp_path) == []


def test_actual_demo_rules_directory_loads_without_error() -> None:
    """Guards against regressions in the real rules/ shipped with the repo."""
    repo_rules_dir = Path(__file__).resolve().parents[3] / "rules"

    rules = load_rules_from_directory(repo_rules_dir)

    assert len(rules) >= 5
    ids = [rule.id for rule in rules]
    assert len(ids) == len(set(ids))
