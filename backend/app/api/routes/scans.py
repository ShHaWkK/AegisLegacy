from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_repository, require_api_key
from app.api.schemas import FindingRead, Page, ScanCreate, ScanRead, ScoreRead
from app.core.config import Settings, get_settings
from app.repositories.models import ScanRecord
from app.repositories.scan_repository import ScanRepository
from app.rules.loader import RuleLoadError
from app.services.scan_service import ScanTargetNotFoundError, run_scan

router = APIRouter(prefix="/scans", tags=["scans"])


def _get_scan_or_404(scan_id: int, repository: ScanRepository) -> ScanRecord:
    scan = repository.get_scan(scan_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan {scan_id} not found"
        )
    return scan


@router.post(
    "",
    response_model=ScanRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_scan(
    payload: ScanCreate,
    repository: ScanRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> ScanRead:
    try:
        outcome = run_scan(
            target_path=Path(payload.target_path),
            rules_dir=settings.rules_dir,
            repository=repository,
        )
    except ScanTargetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RuleLoadError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rules configuration error: {exc}",
        ) from exc

    return ScanRead.model_validate(outcome.scan)


@router.get("", response_model=Page[ScanRead])
def list_scans(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    repository: ScanRepository = Depends(get_repository),
) -> Page[ScanRead]:
    offset = (page - 1) * page_size
    records, total = repository.list_scans(offset=offset, limit=page_size)
    return Page[ScanRead](
        items=[ScanRead.model_validate(record) for record in records],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{scan_id}", response_model=ScanRead)
def get_scan(scan_id: int, repository: ScanRepository = Depends(get_repository)) -> ScanRead:
    scan = _get_scan_or_404(scan_id, repository)
    return ScanRead.model_validate(scan)


@router.get("/{scan_id}/findings", response_model=list[FindingRead])
def get_scan_findings(
    scan_id: int, repository: ScanRepository = Depends(get_repository)
) -> list[FindingRead]:
    _get_scan_or_404(scan_id, repository)
    findings = repository.get_findings(scan_id)
    return [FindingRead.model_validate(finding) for finding in findings]


@router.get("/{scan_id}/score", response_model=ScoreRead)
def get_scan_score(
    scan_id: int, repository: ScanRepository = Depends(get_repository)
) -> ScoreRead:
    scan = _get_scan_or_404(scan_id, repository)
    return ScoreRead(
        score=scan.score, classification=scan.classification, findings_count=scan.findings_count
    )
