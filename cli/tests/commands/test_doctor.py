from __future__ import annotations

from pathlib import Path

from aegislegacy.commands.doctor import run_doctor


def test_run_doctor_all_checks_pass_with_valid_rules_dir(rules_dir: Path) -> None:
    checks = run_doctor(rules_dir)

    assert all(check.passed for check in checks)
    names = {check.name for check in checks}
    assert names == {"Python version", "Rules directory exists", "Rules load without error"}


def test_run_doctor_fails_when_rules_dir_missing(tmp_path: Path) -> None:
    checks = run_doctor(tmp_path / "missing")

    by_name = {check.name: check for check in checks}
    assert by_name["Rules directory exists"].passed is False
    assert by_name["Rules load without error"].passed is False


def test_run_doctor_fails_when_rules_are_invalid(tmp_path: Path) -> None:
    (tmp_path / "bad.yaml").write_text("id: not-a-valid-id\n", encoding="utf-8")

    checks = run_doctor(tmp_path)

    by_name = {check.name: check for check in checks}
    assert by_name["Rules directory exists"].passed is True
    assert by_name["Rules load without error"].passed is False
