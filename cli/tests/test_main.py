from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from aegislegacy.main import app

runner = CliRunner()


def test_scan_command_exits_zero_with_no_critical_findings(
    legacy_project: Path, rules_dir: Path
) -> None:
    result = runner.invoke(
        app, ["scan", str(legacy_project / "clean.py"), "--rules-dir", str(rules_dir)]
    )

    assert result.exit_code == 0
    assert "No findings" in result.stdout


def test_scan_command_reports_findings_and_score(
    legacy_project: Path, rules_dir: Path
) -> None:
    result = runner.invoke(app, ["scan", str(legacy_project), "--rules-dir", str(rules_dir)])

    assert result.exit_code == 0
    assert "PY-EVAL-001" in result.stdout
    assert "Security score" in result.stdout


def test_scan_command_exits_two_on_critical_finding(tmp_path: Path, rules_dir: Path) -> None:
    critical_rule = tmp_path / "critical_rules"
    critical_rule.mkdir()
    (critical_rule / "cmd.yaml").write_text(
        "id: PY-SUBPROC-001\n"
        "language: python\n"
        "severity: critical\n"
        "title: shell=True\n"
        "patterns:\n"
        '  - "shell\\\\s*=\\\\s*True"\n'
        "description: d\n"
        "recommendation: r\n"
        "category: command-injection\n",
        encoding="utf-8",
    )
    project = tmp_path / "proj"
    project.mkdir()
    (project / "run.py").write_text("subprocess.run(cmd, shell=True)\n", encoding="utf-8")

    result = runner.invoke(app, ["scan", str(project), "--rules-dir", str(critical_rule)])

    assert result.exit_code == 2


def test_scan_command_writes_json_output(
    legacy_project: Path, rules_dir: Path, tmp_path: Path
) -> None:
    output_file = tmp_path / "out.json"

    result = runner.invoke(
        app,
        [
            "scan",
            str(legacy_project),
            "--rules-dir",
            str(rules_dir),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert "PY-EVAL-001" in output_file.read_text(encoding="utf-8")


def test_scan_command_fails_on_invalid_rules(legacy_project: Path, tmp_path: Path) -> None:
    bad_rules = tmp_path / "bad_rules"
    bad_rules.mkdir()
    (bad_rules / "bad.yaml").write_text("id: not-valid\n", encoding="utf-8")

    result = runner.invoke(app, ["scan", str(legacy_project), "--rules-dir", str(bad_rules)])

    assert result.exit_code == 1


def test_rules_list_command_prints_rule_table(rules_dir: Path) -> None:
    result = runner.invoke(app, ["rules", "list", "--rules-dir", str(rules_dir)])

    assert result.exit_code == 0
    assert "PY-EVAL-001" in result.stdout


def test_doctor_command_exits_zero_when_healthy(rules_dir: Path) -> None:
    result = runner.invoke(app, ["doctor", "--rules-dir", str(rules_dir)])

    assert result.exit_code == 0
    assert "OK" in result.stdout


def test_doctor_command_exits_one_when_rules_dir_missing(tmp_path: Path) -> None:
    result = runner.invoke(app, ["doctor", "--rules-dir", str(tmp_path / "missing")])

    assert result.exit_code == 1
