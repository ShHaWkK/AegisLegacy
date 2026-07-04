"""Loads and validates rule definitions from YAML files on disk."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from app.rules.schema import RuleDefinition, RuleSchemaError


class RuleLoadError(RuleSchemaError):
    """Raised when a rule file cannot be parsed or fails validation."""


def load_rule_file(path: Path) -> RuleDefinition:
    """Parse and validate a single YAML rule file."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RuleLoadError(f"{path}: invalid YAML ({exc})") from exc

    if not isinstance(raw, dict):
        raise RuleLoadError(f"{path}: rule file must contain a YAML mapping")

    try:
        return RuleDefinition.model_validate(raw)
    except ValidationError as exc:
        raise RuleLoadError(f"{path}: {exc}") from exc


def load_rules_from_directory(directory: Path) -> list[RuleDefinition]:
    """Recursively load every *.yaml/*.yml rule under `directory`.

    Raises RuleLoadError on the first invalid file, or if two rules share
    the same id (ids must be globally unique so findings can be traced
    back unambiguously to the rule that produced them).
    """
    rule_files = sorted(
        [*directory.rglob("*.yaml"), *directory.rglob("*.yml")]
    )

    rules: list[RuleDefinition] = []
    seen_ids: dict[str, Path] = {}
    for rule_file in rule_files:
        rule = load_rule_file(rule_file)
        if rule.id in seen_ids:
            raise RuleLoadError(
                f"{rule_file}: duplicate rule id {rule.id!r} "
                f"(already defined in {seen_ids[rule.id]})"
            )
        seen_ids[rule.id] = rule_file
        rules.append(rule)

    return rules
