from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import rules, scans

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(scans.router)
api_router.include_router(rules.router)
