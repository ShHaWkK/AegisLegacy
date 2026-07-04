from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.repositories.scan_repository import ScanRepository
from app.services.scan_service import ScanTargetNotFoundError, run_scan

_RULE = """
id: PY-EVAL-001
language: python
severity: high
title: Use of eval()
patterns:
  - "\\\\beval\\\\s*\\\\("
description: d
recommendation: r
category: unsafe-eval
"""


@pytest.fixture
def repository() -> ScanRepository:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return ScanRepository(Session(engine))


@pytest.fixture
def rules_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "rules"
    directory.mkdir()
    (directory / "eval.yaml").write_text(_RULE, encoding="utf-8")
    return directory


def test_run_scan_persists_scan_and_findings(
    tmp_path: Path, rules_dir: Path, repository: ScanRepository
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "script.py").write_text("result = eval(user_input)\n", encoding="utf-8")

    outcome = run_scan(target_path=project, rules_dir=rules_dir, repository=repository)

    assert outcome.scan.id is not None
    assert outcome.scan.findings_count == 1
    assert outcome.scan.score == 90.0
    assert len(outcome.findings) == 1

    persisted = repository.get_findings(outcome.scan.id)
    assert len(persisted) == 1
    assert persisted[0].rule_id == "PY-EVAL-001"


def test_run_scan_with_no_findings_gives_perfect_score(
    tmp_path: Path, rules_dir: Path, repository: ScanRepository
) -> None:
    project = tmp_path / "clean"
    project.mkdir()
    (project / "clean.py").write_text("x = 1\n", encoding="utf-8")

    outcome = run_scan(target_path=project, rules_dir=rules_dir, repository=repository)

    assert outcome.scan.score == 100.0
    assert outcome.scan.classification == "Excellent"
    assert outcome.findings == []


def test_run_scan_raises_for_missing_target(
    tmp_path: Path, rules_dir: Path, repository: ScanRepository
) -> None:
    with pytest.raises(ScanTargetNotFoundError):
        run_scan(
            target_path=tmp_path / "does-not-exist",
            rules_dir=rules_dir,
            repository=repository,
        )


def test_run_scan_on_single_file(
    tmp_path: Path, rules_dir: Path, repository: ScanRepository
) -> None:
    file_path = tmp_path / "single.py"
    file_path.write_text("eval(x)\n", encoding="utf-8")

    outcome = run_scan(target_path=file_path, rules_dir=rules_dir, repository=repository)

    assert outcome.scan.findings_count == 1
