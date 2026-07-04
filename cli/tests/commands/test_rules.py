from __future__ import annotations

from pathlib import Path

from aegislegacy.commands.rules import list_rules


def test_list_rules_returns_loaded_rule_definitions(rules_dir: Path) -> None:
    rules = list_rules(rules_dir)

    assert len(rules) == 1
    assert rules[0].id == "PY-EVAL-001"


def test_list_rules_on_empty_directory(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    assert list_rules(empty) == []
