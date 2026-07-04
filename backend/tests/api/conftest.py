"""Test client wired to an isolated in-memory database and rule set.

Deliberately does NOT enter the TestClient as a context manager: that would
trigger the app's lifespan (which calls the *real* get_settings()/init_db()
against the default sqlite file) before our dependency overrides matter.
Plain request/response testing does not need the lifespan to run.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import Settings, get_settings
from app.main import app
from app.repositories.database import get_session

TEST_API_KEY = "test-api-key"

_RULE = """
id: PY-EVAL-001
language: python
severity: high
title: Use of eval()
patterns:
  - "\\\\beval\\\\s*\\\\("
description: d
recommendation: r
category: unsafe-eval
"""


@pytest.fixture
def rules_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "rules"
    directory.mkdir()
    (directory / "eval.yaml").write_text(_RULE, encoding="utf-8")
    return directory


@pytest.fixture
def client(rules_dir: Path) -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    def override_get_settings() -> Settings:
        return Settings(rules_dir=rules_dir, api_key=TEST_API_KEY)

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_settings] = override_get_settings

    yield TestClient(app)

    app.dependency_overrides.clear()
