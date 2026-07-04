"""Doctor command logic: sanity-check the local environment."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from app.rules.loader import RuleLoadError, load_rules_from_directory

MINIMUM_PYTHON = (3, 12)


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    passed: bool
    detail: str


def run_doctor(rules_dir: Path) -> list[DoctorCheck]:
    checks = [_check_python_version(), _check_rules_dir_exists(rules_dir)]
    checks.append(_check_rules_load(rules_dir))
    return checks


def _check_python_version() -> DoctorCheck:
    passed = sys.version_info[:2] >= MINIMUM_PYTHON
    detail = f"Found {sys.version_info.major}.{sys.version_info.minor}, need >= 3.12"
    return DoctorCheck("Python version", passed, detail)


def _check_rules_dir_exists(rules_dir: Path) -> DoctorCheck:
    return DoctorCheck("Rules directory exists", rules_dir.is_dir(), str(rules_dir))


def _check_rules_load(rules_dir: Path) -> DoctorCheck:
    if not rules_dir.is_dir():
        return DoctorCheck("Rules load without error", False, "rules directory missing")
    try:
        rules = load_rules_from_directory(rules_dir)
    except RuleLoadError as exc:
        return DoctorCheck("Rules load without error", False, str(exc))
    return DoctorCheck("Rules load without error", True, f"{len(rules)} rules loaded")
