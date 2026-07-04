from __future__ import annotations

from sqlmodel import Session

from app.repositories.models import FindingRecord
from app.repositories.scan_repository import ScanRepository


def _create_scan(repo: ScanRepository, target: str = "/some/path") -> int:
    scan = repo.create_scan(
        target_path=target, score=80.0, classification="Good", findings_count=1
    )
    assert scan.id is not None
    return scan.id


def test_create_scan_persists_and_assigns_id(session: Session) -> None:
    repo = ScanRepository(session)

    scan = repo.create_scan(
        target_path="/legacy", score=100.0, classification="Excellent", findings_count=0
    )

    assert scan.id is not None
    assert scan.target_path == "/legacy"
    assert scan.status == "completed"


def test_get_scan_returns_none_for_unknown_id(session: Session) -> None:
    repo = ScanRepository(session)

    assert repo.get_scan(999) is None


def test_get_scan_returns_persisted_record(session: Session) -> None:
    repo = ScanRepository(session)
    scan_id = _create_scan(repo)

    scan = repo.get_scan(scan_id)

    assert scan is not None
    assert scan.id == scan_id


def test_add_findings_and_get_findings_round_trip(session: Session) -> None:
    repo = ScanRepository(session)
    scan_id = _create_scan(repo)
    finding = FindingRecord(
        scan_id=0,  # overwritten by add_findings
        rule_id="PY-EVAL-001",
        title="Use of eval",
        severity="high",
        category="unsafe-eval",
        language="python",
        file_path="a.py",
        line_number=3,
        matched_text="eval(x)",
        description="d",
        recommendation="r",
    )

    repo.add_findings(scan_id, [finding])
    findings = repo.get_findings(scan_id)

    assert len(findings) == 1
    assert findings[0].scan_id == scan_id
    assert findings[0].rule_id == "PY-EVAL-001"


def test_get_findings_for_scan_with_no_findings_is_empty(session: Session) -> None:
    repo = ScanRepository(session)
    scan_id = _create_scan(repo)

    assert repo.get_findings(scan_id) == []


def test_list_scans_orders_most_recent_first(session: Session) -> None:
    repo = ScanRepository(session)
    first_id = _create_scan(repo, target="/first")
    second_id = _create_scan(repo, target="/second")

    items, total = repo.list_scans(offset=0, limit=10)

    assert total == 2
    assert [item.id for item in items] == [second_id, first_id]


def test_list_scans_respects_offset_and_limit(session: Session) -> None:
    repo = ScanRepository(session)
    for i in range(5):
        _create_scan(repo, target=f"/target-{i}")

    items, total = repo.list_scans(offset=2, limit=2)

    assert total == 5
    assert len(items) == 2
