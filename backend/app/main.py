"""FastAPI application factory.

Run with: uvicorn app.main:app --reload (see Makefile's run-api target).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.observability.logging import configure_logging
from app.repositories.database import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(level=settings.log_level, json_format=settings.log_format == "json")
    init_db()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="AegisLegacy API",
        description="Scan, score and track legacy Perl/Python codebases.",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.include_router(health_router)
    application.include_router(api_router)
    return application


app = create_app()
