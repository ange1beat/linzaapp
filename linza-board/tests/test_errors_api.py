"""Integration tests for /api/errors endpoints (board#28)."""


def test_report_error_no_auth(client):
    """POST /report accepts errors without authentication (middleware use)."""
    resp = client.post("/api/errors/report", json={
        "service": "linza-board",
        "severity": "error",
        "message": "test error",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "recorded"
    assert "id" in data


def test_list_errors_requires_auth(client):
    """GET / requires admin auth."""
    resp = client.get("/api/errors/")
    assert resp.status_code == 401


def test_list_errors(client, auth_headers):
    """GET / returns reported errors."""
    client.post("/api/errors/report", json={
        "service": "test-svc", "severity": "warning", "message": "warn msg",
    })
    resp = client.get("/api/errors/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(e["message"] == "warn msg" for e in data["errors"])


def test_list_errors_filter_service(client, auth_headers):
    """GET /?service= filters by service name."""
    client.post("/api/errors/report", json={"service": "svc-a", "message": "a"})
    client.post("/api/errors/report", json={"service": "svc-b", "message": "b"})
    resp = client.get("/api/errors/?service=svc-a", headers=auth_headers)
    assert resp.status_code == 200
    for e in resp.json()["errors"]:
        assert e["service"] == "svc-a"


def test_list_errors_filter_severity(client, auth_headers):
    """GET /?severity= filters by severity."""
    client.post("/api/errors/report", json={"severity": "critical", "message": "crit"})
    client.post("/api/errors/report", json={"severity": "warning", "message": "warn"})
    resp = client.get("/api/errors/?severity=critical", headers=auth_headers)
    assert resp.status_code == 200
    for e in resp.json()["errors"]:
        assert e["severity"] == "critical"


def test_list_errors_pagination(client, auth_headers):
    """GET /?limit=&offset= paginates correctly."""
    for i in range(5):
        client.post("/api/errors/report", json={"message": f"err-{i}"})
    resp = client.get("/api/errors/?limit=2&offset=0", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["errors"]) == 2
    assert data["total"] >= 5


def test_stats(client, auth_headers):
    """GET /stats returns aggregate statistics."""
    client.post("/api/errors/report", json={
        "service": "linza-board", "severity": "error", "message": "stat test",
    })
    resp = client.get("/api/errors/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert "last_hour" in data
    assert "by_service" in data
    assert "by_severity" in data


def test_manual_error(client, auth_headers):
    """POST /manual creates error from UI form."""
    resp = client.post("/api/errors/manual", json={
        "service": "linza-board",
        "severity": "warning",
        "category": "ui",
        "message": "Manual bug report",
        "description": "Steps to reproduce...",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"


def test_manual_error_with_github(client, auth_headers):
    """POST /manual with submit_github=true returns github_issue_url."""
    resp = client.post("/api/errors/manual", json={
        "message": "GitHub test",
        "submit_github": True,
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "github_issue_url" in data
    assert "github.com" in data["github_issue_url"]


def test_submit_issue(client, auth_headers):
    """POST /{id}/submit-issue marks error as submitted."""
    create = client.post("/api/errors/report", json={"message": "to submit"})
    error_id = create.json()["id"]

    resp = client.post(f"/api/errors/{error_id}/submit-issue", json={
        "github_issue_url": "https://github.com/test/repo/issues/1",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "submitted"


def test_submit_issue_not_found(client, auth_headers):
    """POST /{id}/submit-issue returns 404 for missing error."""
    resp = client.post("/api/errors/99999/submit-issue", json={
        "github_issue_url": "https://github.com/test/repo/issues/1",
    }, headers=auth_headers)
    assert resp.status_code == 404


def test_clear_errors(client, auth_headers):
    """DELETE / clears all errors."""
    client.post("/api/errors/report", json={"message": "to clear"})
    resp = client.delete("/api/errors/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["deleted"] >= 1

    listing = client.get("/api/errors/", headers=auth_headers)
    assert listing.json()["total"] == 0


def test_clear_errors_by_service(client, auth_headers):
    """DELETE /?service= clears only matching service."""
    client.post("/api/errors/report", json={"service": "keep", "message": "keep"})
    client.post("/api/errors/report", json={"service": "remove", "message": "del"})

    resp = client.delete("/api/errors/?service=remove", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["deleted"] >= 1

    listing = client.get("/api/errors/", headers=auth_headers)
    services = {e["service"] for e in listing.json()["errors"]}
    assert "remove" not in services
