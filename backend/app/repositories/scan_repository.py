"""Persistence operations for scans and their findings.

This is the only module allowed to run SQL against the scans/findings
tables — services depend on this repository rather than on SQLModel
sessions directly, so the storage layer can be swapped without touching
business logic.
"""

from __future__ import annotations

from sqlmodel import Session, func, select

from app.repositories.models import FindingRecord, ScanRecord


class ScanRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_scan(
        self, *, target_path: str, score: float, classification: str, findings_count: int
    ) -> ScanRecord:
        scan = ScanRecord(
            target_path=target_path,
            score=score,
            classification=classification,
            findings_count=findings_count,
        )
        self._session.add(scan)
        self._session.commit()
        self._session.refresh(scan)
        return scan

    def add_findings(self, scan_id: int, findings: list[FindingRecord]) -> None:
        for finding in findings:
            finding.scan_id = scan_id
            self._session.add(finding)
        self._session.commit()

    def get_scan(self, scan_id: int) -> ScanRecord | None:
        return self._session.get(ScanRecord, scan_id)

    def list_scans(self, *, offset: int, limit: int) -> tuple[list[ScanRecord], int]:
        total = self._session.exec(select(func.count()).select_from(ScanRecord)).one()
        statement = (
            select(ScanRecord).order_by(ScanRecord.created_at.desc()).offset(offset).limit(limit)
        )
        items = list(self._session.exec(statement))
        return items, total

    def get_findings(self, scan_id: int) -> list[FindingRecord]:
        statement = select(FindingRecord).where(FindingRecord.scan_id == scan_id)
        return list(self._session.exec(statement))
