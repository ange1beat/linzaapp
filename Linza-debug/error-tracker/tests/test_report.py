"""Tests for POST /api/errors/report — validation, defaults, all fields."""


class TestReportValidation:
    """Input validation and defaults."""

    def test_minimal_payload(self, client):
        resp = client.post("/api/errors/report", json={"message": "err"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "recorded"
        assert isinstance(data["id"], int)

    def test_missing_message_returns_422(self, client):
        resp = client.post("/api/errors/report", json={"service": "test"})
        assert resp.status_code == 422

    def test_empty_body_returns_422(self, client):
        resp = client.post("/api/errors/report", json={})
        assert resp.status_code == 422

    def test_defaults_applied(self, client):
        resp = client.post("/api/errors/report", json={"message": "test"})
        error_id = resp.json()["id"]

        errors = client.get("/api/errors").json()["errors"]
        rec = next(e for e in errors if e["id"] == error_id)
        assert rec["service"] == "unknown"
        assert rec["severity"] == "error"
        assert rec["category"] == "api"  # default for unknown service

    def test_all_fields_stored(self, client):
        payload = {
            "service": "linza-board",
            "severity": "critical",
            "category": "auth",
            "message": "Token expired",
            "traceback": "Traceback...",
            "endpoint": "/api/auth/me",
            "method": "GET",
            "status_code": 401,
            "request_id": "abc123",
            "extra": '{"user_id": 42}',
        }
        resp = client.post("/api/errors/report", json=payload)
        error_id = resp.json()["id"]

        errors = client.get("/api/errors").json()["errors"]
        rec = next(e for e in errors if e["id"] == error_id)
        assert rec["service"] == "linza-board"
        assert rec["severity"] == "critical"
        assert rec["category"] == "auth"
        assert rec["message"] == "Token expired"
        assert rec["traceback"] == "Traceback..."
        assert rec["endpoint"] == "/api/auth/me"
        assert rec["method"] == "GET"
        assert rec["status_code"] == 401
        assert rec["request_id"] == "abc123"
        assert rec["extra"] == '{"user_id": 42}'

    def test_optional_fields_null(self, client):
        resp = client.post("/api/errors/report", json={"message": "bare"})
        error_id = resp.json()["id"]

        errors = client.get("/api/errors").json()["errors"]
        rec = next(e for e in errors if e["id"] == error_id)
        assert rec["traceback"] is None
        assert rec["endpoint"] is None
        assert rec["method"] is None
        assert rec["status_code"] is None
        assert rec["request_id"] is None
        assert rec["extra"] is None

    def test_created_at_populated(self, client):
        resp = client.post("/api/errors/report", json={"message": "ts test"})
        error_id = resp.json()["id"]

        errors = client.get("/api/errors").json()["errors"]
        rec = next(e for e in errors if e["id"] == error_id)
        assert rec["created_at"] is not None

    def test_multiple_reports_get_unique_ids(self, client):
        ids = set()
        for i in range(5):
            resp = client.post("/api/errors/report", json={"message": f"err {i}"})
            ids.add(resp.json()["id"])
        assert len(ids) == 5
