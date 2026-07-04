"""Orchestrates a scan: run the rules engine, score it, persist the result.

The core edition runs scans synchronously within the request — there is no
worker queue (see ROADMAP.md's scope decisions). For the directory sizes a
demo/portfolio target realistically has, this keeps the whole stack simple
and fully testable without Celery/Redis.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.repositories.models import FindingRecord, ScanRecord
from app.repositories.scan_repository import ScanRepository
from app.rules.engine import RuleEngine
from app.rules.loader import load_rules_from_directory
from app.services.scoring import compute_score


class ScanTargetNotFoundError(Exception):
    """Raised when the requested scan target does not exist on disk."""


@dataclass(frozen=True)
class ScanOutcome:
    scan: ScanRecord
    findings: list[FindingRecord]


def run_scan(
    *, target_path: Path, rules_dir: Path, repository: ScanRepository
) -> ScanOutcome:
    if not target_path.exists():
        raise ScanTargetNotFoundError(f"Scan target does not exist: {target_path}")

    rules = load_rules_from_directory(rules_dir)
    engine = RuleEngine(rules)

    if target_path.is_dir():
        findings = engine.scan_tree(target_path)
    else:
        findings = engine.scan_file(target_path, root=target_path.parent)

    score = compute_score(findings)

    scan = repository.create_scan(
        target_path=str(target_path),
        score=score.score,
        classification=score.classification,
        findings_count=len(findings),
    )
    # create_scan commits and refreshes the record, so the primary key is
    # always populated by the time we get here.
    assert scan.id is not None
    scan_id = scan.id

    finding_records = [
        FindingRecord(
            scan_id=scan_id,
            rule_id=finding.rule_id,
            title=finding.title,
            severity=finding.severity.value,
            category=finding.category,
            language=finding.language,
            file_path=finding.file_path,
            line_number=finding.line_number,
            matched_text=finding.matched_text,
            description=finding.description,
            recommendation=finding.recommendation,
        )
        for finding in findings
    ]
    if finding_records:
        repository.add_findings(scan_id, finding_records)

    return ScanOutcome(scan=scan, findings=finding_records)
