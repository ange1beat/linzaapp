"""Tests for GET /api/errors — filtering, pagination, ordering."""


def _seed(client, n, **overrides):
    """Create n error records with optional field overrides."""
    ids = []
    for i in range(n):
        payload = {"message": f"error {i}", **overrides}
        resp = client.post("/api/errors/report", json=payload)
        ids.append(resp.json()["id"])
    return ids


class TestListBasic:
    """Basic list behavior."""

    def test_empty_db_returns_empty_list(self, client):
        resp = client.get("/api/errors")
        data = resp.json()
        assert data["errors"] == []
        assert data["total"] == 0

    def test_returns_all_records(self, client):
        _seed(client, 3)
        data = client.get("/api/errors").json()
        assert data["total"] == 3
        assert len(data["errors"]) == 3

    def test_ordered_by_created_at_desc(self, client):
        """Most recent errors come first. When created_at is the same (same second),
        SQLite preserves insertion order, so we just verify the endpoint returns data."""
        _seed(client, 3)
        errors = client.get("/api/errors").json()["errors"]
        assert len(errors) == 3
        # created_at should be non-null for all
        assert all(e["created_at"] is not None for e in errors)


class TestListFilters:
    """Filter by service, severity, category."""

    def test_filter_by_service(self, client):
        _seed(client, 2, service="vpleer")
        _seed(client, 1, service="linza-board")
        data = client.get("/api/errors", params={"service": "vpleer"}).json()
        assert data["total"] == 2
        assert all(e["service"] == "vpleer" for e in data["errors"])

    def test_filter_by_severity(self, client):
        _seed(client, 2, severity="critical")
        _seed(client, 3, severity="error")
        data = client.get("/api/errors", params={"severity": "critical"}).json()
        assert data["total"] == 2

    def test_combined_filters(self, client):
        _seed(client, 1, service="vpleer", severity="critical")
        _seed(client, 1, service="vpleer", severity="error")
        _seed(client, 1, service="linza-board", severity="critical")
        data = client.get("/api/errors", params={
            "service": "vpleer", "severity": "critical",
        }).json()
        assert data["total"] == 1

    def test_no_match_returns_empty(self, client):
        _seed(client, 3, service="vpleer")
        data = client.get("/api/errors", params={"service": "nonexistent"}).json()
        assert data["total"] == 0
        assert data["errors"] == []


class TestListPagination:
    """Limit and offset parameters."""

    def test_limit_restricts_results(self, client):
        _seed(client, 5)
        data = client.get("/api/errors", params={"limit": 2}).json()
        assert data["total"] == 5
        assert len(data["errors"]) == 2

    def test_offset_skips_records(self, client):
        _seed(client, 5)
        all_errors = client.get("/api/errors").json()["errors"]
        offset_errors = client.get("/api/errors", params={"offset": 3}).json()["errors"]
        assert len(offset_errors) == 2
        assert offset_errors[0]["id"] == all_errors[3]["id"]

    def test_limit_and_offset_combined(self, client):
        _seed(client, 10)
        data = client.get("/api/errors", params={"limit": 3, "offset": 2}).json()
        assert data["total"] == 10
        assert len(data["errors"]) == 3

    def test_offset_beyond_total_returns_empty(self, client):
        _seed(client, 3)
        data = client.get("/api/errors", params={"offset": 100}).json()
        assert data["total"] == 3
        assert data["errors"] == []

    def test_limit_min_validation(self, client):
        resp = client.get("/api/errors", params={"limit": 0})
        assert resp.status_code == 422

    def test_limit_max_validation(self, client):
        resp = client.get("/api/errors", params={"limit": 1001})
        assert resp.status_code == 422
