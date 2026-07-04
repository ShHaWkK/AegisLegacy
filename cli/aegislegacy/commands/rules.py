"""Rules command logic: list the detection rules currently loaded."""

from __future__ import annotations

from pathlib import Path

from app.rules.loader import load_rules_from_directory
from app.rules.schema import RuleDefinition


def list_rules(rules_dir: Path) -> list[RuleDefinition]:
    return load_rules_from_directory(rules_dir)
