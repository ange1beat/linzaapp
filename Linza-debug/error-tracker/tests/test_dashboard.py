"""Tests for GET /api/dashboard — aggregation statistics."""


def _seed(client, n, **overrides):
    for i in range(n):
        client.post("/api/errors/report", json={"message": f"e{i}", **overrides})


class TestDashboard:

    def test_empty_db(self, client):
        data = client.get("/api/dashboard").json()
        assert data["total"] == 0
        assert data["last_hour"] == 0
        assert data["by_service"] == {}
        assert data["by_severity"] == {}
        assert data["by_category"] == {}

    def test_total_count(self, client):
        _seed(client, 5)
        assert client.get("/api/dashboard").json()["total"] == 5

    def test_last_hour_includes_recent(self, client):
        _seed(client, 3)
        data = client.get("/api/dashboard").json()
        assert data["last_hour"] == 3

    def test_by_service_breakdown(self, client):
        _seed(client, 2, service="vpleer")
        _seed(client, 3, service="linza-board")
        data = client.get("/api/dashboard").json()
        assert data["by_service"]["vpleer"] == 2
        assert data["by_service"]["linza-board"] == 3

    def test_by_severity_breakdown(self, client):
        _seed(client, 1, severity="critical")
        _seed(client, 4, severity="error")
        data = client.get("/api/dashboard").json()
        assert data["by_severity"]["critical"] == 1
        assert data["by_severity"]["error"] == 4

    def test_by_category_breakdown(self, client):
        _seed(client, 2, service="vpleer")        # → player
        _seed(client, 1, category="ui")            # explicit
        _seed(client, 3, service="linza-board")    # → api
        data = client.get("/api/dashboard").json()
        assert data["by_category"]["player"] == 2
        assert data["by_category"]["ui"] == 1
        assert data["by_category"]["api"] == 3
