"""FastAPI dependency providers, kept thin: they wire other layers together
without containing business logic themselves.
"""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.repositories.database import get_session
from app.repositories.scan_repository import ScanRepository
from app.security.api_key import verify_api_key


def get_repository(session: Session = Depends(get_session)) -> ScanRepository:
    return ScanRepository(session)


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    if not verify_api_key(x_api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
