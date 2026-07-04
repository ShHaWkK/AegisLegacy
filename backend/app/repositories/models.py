"""SQLModel table models — the only place that knows about database columns.

These are persistence models, deliberately separate from the domain
`Finding`/`Severity` types: the domain layer must stay importable without a
database dependency, and the API schemas (app/api/schemas.py) are separate
again so the wire format can evolve independently of the storage format.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class ScanRecord(SQLModel, table=True):
    __tablename__ = "scans"

    id: int | None = Field(default=None, primary_key=True)
    target_path: str
    status: str = Field(default="completed")
    score: float
    classification: str
    findings_count: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class FindingRecord(SQLModel, table=True):
    __tablename__ = "findings"

    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scans.id", index=True)
    rule_id: str
    title: str
    severity: str
    category: str
    language: str
    file_path: str
    line_number: int
    matched_text: str
    description: str
    recommendation: str
