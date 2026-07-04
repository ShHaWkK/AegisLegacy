from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

# Kept in sync with tests/api/conftest.py's `client` fixture.
TEST_API_KEY = "test-api-key"


def _auth_headers() -> dict[str, str]:
    return {"X-API-Key": TEST_API_KEY}


def test_create_scan_requires_api_key(client: TestClient, tmp_path: Path) -> None:
    response = client.post("/api/v1/scans", json={"target_path": str(tmp_path)})

    assert response.status_code == 401


def test_create_scan_rejects_wrong_api_key(client: TestClient, tmp_path: Path) -> None:
    response = client.post(
        "/api/v1/scans",
        json={"target_path": str(tmp_path)},
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401


def test_create_scan_returns_findings_and_score(client: TestClient, tmp_path: Path) -> None:
    (tmp_path / "script.py").write_text("result = eval(user_input)\n", encoding="utf-8")

    response = client.post(
        "/api/v1/scans", json={"target_path": str(tmp_path)}, headers=_auth_headers()
    )

    assert response.status_code == 201
    body = response.json()
    assert body["findings_count"] == 1
    assert body["score"] == 90.0
    assert body["classification"] == "Good"
    assert "id" in body


def test_create_scan_for_missing_target_returns_404(client: TestClient, tmp_path: Path) -> None:
    response = client.post(
        "/api/v1/scans",
        json={"target_path": str(tmp_path / "missing")},
        headers=_auth_headers(),
    )

    assert response.status_code == 404


def test_get_scan_returns_persisted_scan(client: TestClient, tmp_path: Path) -> None:
    create_response = client.post(
        "/api/v1/scans", json={"target_path": str(tmp_path)}, headers=_auth_headers()
    )
    scan_id = create_response.json()["id"]

    response = client.get(f"/api/v1/scans/{scan_id}")

    assert response.status_code == 200
    assert response.json()["id"] == scan_id


def test_get_scan_returns_404_for_unknown_id(client: TestClient) -> None:
    response = client.get("/api/v1/scans/999")

    assert response.status_code == 404


def test_get_scan_findings(client: TestClient, tmp_path: Path) -> None:
    (tmp_path / "script.py").write_text("eval(x)\n", encoding="utf-8")
    scan_id = client.post(
        "/api/v1/scans", json={"target_path": str(tmp_path)}, headers=_auth_headers()
    ).json()["id"]

    response = client.get(f"/api/v1/scans/{scan_id}/findings")

    assert response.status_code == 200
    findings = response.json()
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "PY-EVAL-001"


def test_get_scan_findings_returns_404_for_unknown_scan(client: TestClient) -> None:
    response = client.get("/api/v1/scans/999/findings")

    assert response.status_code == 404


def test_get_scan_score(client: TestClient, tmp_path: Path) -> None:
    scan_id = client.post(
        "/api/v1/scans", json={"target_path": str(tmp_path)}, headers=_auth_headers()
    ).json()["id"]

    response = client.get(f"/api/v1/scans/{scan_id}/score")

    assert response.status_code == 200
    assert response.json() == {"score": 100.0, "classification": "Excellent", "findings_count": 0}


def test_get_scan_score_returns_404_for_unknown_scan(client: TestClient) -> None:
    response = client.get("/api/v1/scans/999/score")

    assert response.status_code == 404


def test_list_scans_is_paginated_and_ordered_most_recent_first(
    client: TestClient, tmp_path: Path
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    client.post("/api/v1/scans", json={"target_path": str(first)}, headers=_auth_headers())
    client.post("/api/v1/scans", json={"target_path": str(second)}, headers=_auth_headers())

    response = client.get("/api/v1/scans?page=1&page_size=1")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["target_path"] == str(second)


def test_list_scans_empty_by_default(client: TestClient) -> None:
    response = client.get("/api/v1/scans")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "page": 1, "page_size": 20}
