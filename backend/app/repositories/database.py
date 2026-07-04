"""Database engine and session management.

The core edition uses SQLite with SQLModel and `metadata.create_all` at
startup instead of migrations — acceptable for a single-table-family,
pre-production tool. A migration tool (Alembic) is the natural upgrade path
once the schema needs to evolve under real data (see ROADMAP.md).
"""

from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    connect_args = (
        {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    )
    return create_engine(settings.database_url, connect_args=connect_args)


def init_db(engine: Engine | None = None) -> None:
    """Create all tables. Safe to call repeatedly (no-op on existing tables)."""
    SQLModel.metadata.create_all(engine or get_engine())


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
