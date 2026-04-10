"""Tests for debug#11: date range and endpoint filters on GET /api/errors."""

from datetime import datetime, timedelta, timezone

from app.main import ErrorRecord, SessionLocal


def _seed(client, **overrides):
    payload = {"message": "test error", **overrides}
    return client.post("/api/errors/report", json=payload).json()["id"]


def _create_error_at(dt, service="test", endpoint=None):
    """Insert error record with a specific created_at timestamp (naive UTC)."""
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    db = SessionLocal()
    try:
        record = ErrorRecord(
            service=service,
            severity="error",
            category="api",
            message="dated error",
            endpoint=endpoint,
            created_at=dt,
        )
        db.add(record)
        db.commit()
    finally:
        db.close()


class TestEndpointFilter:
    """Filter by endpoint (substring match)."""

    def test_filter_by_endpoint_exact(self, client):
        _seed(client, endpoint="/api/files/upload")
        _seed(client, endpoint="/api/auth/login")
        data = client.get("/api/errors", params={"endpoint": "/api/files/upload"}).json()
        assert data["total"] == 1
        assert data["errors"][0]["endpoint"] == "/api/files/upload"

    def test_filter_by_endpoint_contains(self, client):
        _seed(client, endpoint="/api/files/upload")
        _seed(client, endpoint="/api/files/download/video.mp4")
        _seed(client, endpoint="/api/auth/login")
        data = client.get("/api/errors", params={"endpoint": "/api/files"}).json()
        assert data["total"] == 2

    def test_filter_by_endpoint_no_match(self, client):
        _seed(client, endpoint="/api/auth/login")
        data = client.get("/api/errors", params={"endpoint": "/api/vpleer"}).json()
        assert data["total"] == 0

    def test_filter_endpoint_null_records_excluded(self, client):
        """Errors with endpoint=None should not match any endpoint filter."""
        _seed(client)  # no endpoint → NULL
        _seed(client, endpoint="/api/files/upload")
        data = client.get("/api/errors", params={"endpoint": "/api/files"}).json()
        assert data["total"] == 1

    def test_filter_endpoint_empty_string_returns_all(self, client):
        """Empty endpoint param is falsy → no filter applied."""
        _seed(client, endpoint="/api/files/upload")
        _seed(client, endpoint="/api/auth/login")
        data = client.get("/api/errors", params={"endpoint": ""}).json()
        assert data["total"] == 2


class TestDateFilter:
    """Filter by from_date and to_date (ISO 8601)."""

    def test_from_date_filters_old_errors(self, client):
        now = datetime.utcnow()
        _create_error_at(now - timedelta(days=5))
        _create_error_at(now - timedelta(days=1))
        _create_error_at(now)

        cutoff = (now - timedelta(days=2)).isoformat()
        data = client.get("/api/errors", params={"from_date": cutoff}).json()
        assert data["total"] == 2

    def test_to_date_filters_recent_errors(self, client):
        now = datetime.utcnow()
        _create_error_at(now - timedelta(days=5))
        _create_error_at(now - timedelta(days=3))
        _create_error_at(now)

        cutoff = (now - timedelta(days=2)).isoformat()
        data = client.get("/api/errors", params={"to_date": cutoff}).json()
        assert data["total"] == 2

    def test_date_range(self, client):
        now = datetime.utcnow()
        _create_error_at(now - timedelta(days=10))
        _create_error_at(now - timedelta(days=5))
        _create_error_at(now - timedelta(days=3))
        _create_error_at(now)

        from_dt = (now - timedelta(days=6)).isoformat()
        to_dt = (now - timedelta(days=2)).isoformat()
        data = client.get("/api/errors", params={
            "from_date": from_dt,
            "to_date": to_dt,
        }).json()
        assert data["total"] == 2

    def test_boundary_from_date_inclusive(self, client):
        """Record exactly at from_date should be included (>=)."""
        exact_time = datetime(2026, 3, 15, 12, 0, 0)
        _create_error_at(exact_time)
        data = client.get("/api/errors", params={
            "from_date": exact_time.isoformat(),
        }).json()
        assert data["total"] == 1

    def test_boundary_to_date_inclusive(self, client):
        """Record exactly at to_date should be included (<=)."""
        exact_time = datetime(2026, 3, 15, 12, 0, 0)
        _create_error_at(exact_time)
        data = client.get("/api/errors", params={
            "to_date": exact_time.isoformat(),
        }).json()
        assert data["total"] == 1

    def test_timezone_aware_date_converted_to_utc(self, client):
        """Timezone-aware ISO date should be normalized to UTC for comparison."""
        now = datetime.utcnow()
        _create_error_at(now - timedelta(hours=1))
        _create_error_at(now)

        # Send timezone-aware cutoff (UTC+3 = UTC-aware after conversion)
        cutoff_utc = now - timedelta(hours=2)
        cutoff_plus3 = cutoff_utc.replace(tzinfo=timezone(timedelta(hours=3))) + timedelta(hours=3)
        data = client.get("/api/errors", params={
            "from_date": cutoff_plus3.isoformat(),
        }).json()
        assert data["total"] == 2

    def test_invalid_date_ignored(self, client):
        _seed(client)
        data = client.get("/api/errors", params={"from_date": "not-a-date"}).json()
        assert data["total"] == 1

    def test_empty_date_string_ignored(self, client):
        """Empty from_date/to_date should be falsy → no filter."""
        _seed(client)
        data = client.get("/api/errors", params={"from_date": "", "to_date": ""}).json()
        assert data["total"] == 1

    def test_combined_date_and_service(self, client):
        now = datetime.utcnow()
        _create_error_at(now - timedelta(days=5), service="vpleer")
        _create_error_at(now, service="vpleer")
        _create_error_at(now, service="storage")

        cutoff = (now - timedelta(days=1)).isoformat()
        data = client.get("/api/errors", params={
            "service": "vpleer",
            "from_date": cutoff,
        }).json()
        assert data["total"] == 1
        assert data["errors"][0]["service"] == "vpleer"

    def test_combined_date_and_endpoint(self, client):
        now = datetime.utcnow()
        _create_error_at(now - timedelta(days=5), endpoint="/api/files/upload")
        _create_error_at(now, endpoint="/api/files/download")
        _create_error_at(now, endpoint="/api/auth/login")

        cutoff = (now - timedelta(days=1)).isoformat()
        data = client.get("/api/errors", params={
            "endpoint": "/api/files",
            "from_date": cutoff,
        }).json()
        assert data["total"] == 1
        assert "/api/files" in data["errors"][0]["endpoint"]
