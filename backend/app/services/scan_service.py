"""Orchestre un scan : lance le moteur de règles, calcule le score, persiste.

L'édition core exécute les scans de façon synchrone dans la requête — pas de
file d'attente (voir les choix de scope dans ROADMAP.md). Pour la taille de
dossier réaliste d'une démo/portfolio, ça garde toute la stack simple et
testable sans Celery/Redis.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.repositories.models import FindingRecord, ScanRecord
from app.repositories.scan_repository import ScanRepository
from app.services.scan_runner import ScanTargetNotFoundError, execute_scan

__all__ = ["ScanOutcome", "ScanTargetNotFoundError", "run_scan"]


@dataclass(frozen=True)
class ScanOutcome:
    scan: ScanRecord
    findings: list[FindingRecord]


def run_scan(
    *, target_path: Path, rules_dir: Path, repository: ScanRepository
) -> ScanOutcome:
    findings, score = execute_scan(target_path, rules_dir)

    scan = repository.create_scan(
        target_path=str(target_path),
        score=score.score,
        classification=score.classification,
        findings_count=len(findings),
    )
    # create_scan commits et rafraîchit l'enregistrement : la clé primaire
    # est donc forcément déjà renseignée à ce stade.
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
