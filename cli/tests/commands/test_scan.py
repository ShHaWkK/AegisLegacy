from __future__ import annotations

from pathlib import Path

import pytest

from aegislegacy.commands.scan import ScanTargetNotFoundError, perform_scan


def test_perform_scan_detects_findings_in_directory(
    legacy_project: Path, rules_dir: Path
) -> None:
    findings, score = perform_scan(legacy_project, rules_dir)

    assert len(findings) == 1
    assert findings[0].rule_id == "PY-EVAL-001"
    assert findings[0].file_path == "script.py"
    assert score.score == pytest.approx(90.0)


def test_perform_scan_on_single_file(legacy_project: Path, rules_dir: Path) -> None:
    findings, _ = perform_scan(legacy_project / "script.py", rules_dir)

    assert len(findings) == 1


def test_perform_scan_with_no_findings_gives_perfect_score(
    legacy_project: Path, rules_dir: Path
) -> None:
    findings, score = perform_scan(legacy_project / "clean.py", rules_dir)

    assert findings == []
    assert score.score == 100.0
    assert score.classification == "Excellent"


def test_perform_scan_raises_for_missing_target(tmp_path: Path, rules_dir: Path) -> None:
    with pytest.raises(ScanTargetNotFoundError):
        perform_scan(tmp_path / "does-not-exist", rules_dir)
