from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_list_rules_returns_loaded_rules(client: TestClient) -> None:
    response = client.get("/api/v1/rules")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == "PY-EVAL-001"


def test_list_rules_with_broken_rules_dir_returns_500(
    client: TestClient, rules_dir: Path
) -> None:
    (rules_dir / "broken.yaml").write_text("id: not-valid\n", encoding="utf-8")

    response = client.get("/api/v1/rules")

    assert response.status_code == 500
