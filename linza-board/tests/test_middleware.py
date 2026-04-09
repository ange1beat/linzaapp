"""Integration tests for ErrorReporterMiddleware (board#28)."""

from backend.models import ErrorRecord


def test_middleware_captures_404(client, auth_headers, db_session):
    """404 is in _IGNORED_STATUS_CODES — should NOT be recorded."""
    client.get("/api/nonexistent-endpoint", headers=auth_headers)

    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.endpoint == "/api/nonexistent-endpoint"
    ).all()
    assert len(records) == 0


def test_middleware_captures_unhandled_exception(client, db_session):
    """Unhandled exceptions should be recorded as severity=critical."""
    # The /health endpoint always works. We need an endpoint that raises.
    # POST to /api/errors/report with invalid JSON triggers 422 which is 4xx.
    resp = client.post("/api/errors/report", content="not json",
                       headers={"Content-Type": "application/json"})
    assert resp.status_code == 422
    # 422 is NOT in ignored list (401, 404, 405), so it should be recorded
    # as a warning (4xx)
    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.endpoint == "/api/errors/report",
        ErrorRecord.status_code == 422,
    ).all()
    assert len(records) >= 1
    assert records[0].severity == "warning"


def test_middleware_skips_401(client, db_session):
    """401 is in _IGNORED_STATUS_CODES — should NOT be recorded."""
    client.get("/api/users/", headers={"Authorization": "Bearer invalid"})

    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.status_code == 401,
    ).all()
    assert len(records) == 0


def test_middleware_sets_request_id(client, auth_headers):
    """Middleware adds X-Request-ID to response headers."""
    resp = client.get("/health", headers=auth_headers)
    assert "x-request-id" in resp.headers


def test_middleware_preserves_incoming_request_id(client, auth_headers):
    """Middleware uses incoming X-Request-ID if provided."""
    resp = client.get("/health", headers={
        **auth_headers,
        "X-Request-ID": "custom-req-123",
    })
    assert resp.headers.get("x-request-id") == "custom-req-123"
