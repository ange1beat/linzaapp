"""Tests for category field: auto-inference, filtering, dashboard stats."""

from app.main import infer_category


class TestInferCategory:
    """Unit tests for infer_category()."""

    def test_explicit_overrides_service(self):
        assert infer_category("vpleer", "ui") == "ui"

    def test_vpleer_maps_to_player(self):
        assert infer_category("vpleer") == "player"

    def test_storage_service_maps_to_storage(self):
        assert infer_category("storage-service") == "storage"

    def test_analytics_service_maps_to_analytics(self):
        assert infer_category("analytics-service") == "analytics"

    def test_linza_board_maps_to_api(self):
        assert infer_category("linza-board") == "api"

    def test_unknown_service_defaults_to_api(self):
        assert infer_category("unknown-svc") == "api"

    def test_none_explicit_triggers_inference(self):
        assert infer_category("vpleer", None) == "player"

    def test_empty_string_explicit_triggers_inference(self):
        assert infer_category("vpleer", "") == "player"


class TestReportWithCategory:
    """POST /api/errors/report — category handling."""

    def test_explicit_category_stored(self, client):
        resp = client.post("/api/errors/report", json={
            "service": "linza-board",
            "message": "test error",
            "category": "ui",
        })
        assert resp.status_code == 200
        error_id = resp.json()["id"]

        errors = client.get("/api/errors").json()["errors"]
        record = next(e for e in errors if e["id"] == error_id)
        assert record["category"] == "ui"

    def test_auto_infer_vpleer(self, client):
        resp = client.post("/api/errors/report", json={
            "service": "vpleer",
            "message": "video error",
        })
        error_id = resp.json()["id"]

        errors = client.get("/api/errors").json()["errors"]
        record = next(e for e in errors if e["id"] == error_id)
        assert record["category"] == "player"

    def test_auto_infer_storage(self, client):
        resp = client.post("/api/errors/report", json={
            "service": "storage-service",
            "message": "s3 error",
        })
        error_id = resp.json()["id"]

        errors = client.get("/api/errors").json()["errors"]
        record = next(e for e in errors if e["id"] == error_id)
        assert record["category"] == "storage"

    def test_auto_infer_unknown_defaults_api(self, client):
        resp = client.post("/api/errors/report", json={
            "service": "mystery-svc",
            "message": "unknown",
        })
        error_id = resp.json()["id"]

        errors = client.get("/api/errors").json()["errors"]
        record = next(e for e in errors if e["id"] == error_id)
        assert record["category"] == "api"


class TestFilterByCategory:
    """GET /api/errors?category=... filtering."""

    def test_filter_returns_matching(self, client):
        client.post("/api/errors/report", json={
            "service": "linza-board", "message": "err1", "category": "ui",
        })
        client.post("/api/errors/report", json={
            "service": "vpleer", "message": "err2",
        })

        resp = client.get("/api/errors", params={"category": "ui"})
        data = resp.json()
        assert data["total"] == 1
        assert data["errors"][0]["category"] == "ui"

    def test_filter_nonexistent_returns_empty(self, client):
        client.post("/api/errors/report", json={
            "service": "vpleer", "message": "err",
        })
        resp = client.get("/api/errors", params={"category": "auth"})
        assert resp.json()["total"] == 0


class TestDashboardCategory:
    """GET /api/dashboard — by_category stats."""

    def test_by_category_present(self, client):
        client.post("/api/errors/report", json={
            "service": "vpleer", "message": "e1",
        })
        client.post("/api/errors/report", json={
            "service": "vpleer", "message": "e2",
        })
        client.post("/api/errors/report", json={
            "service": "linza-board", "message": "e3", "category": "ui",
        })

        resp = client.get("/api/dashboard")
        data = resp.json()
        assert "by_category" in data
        assert data["by_category"]["player"] == 2
        assert data["by_category"]["ui"] == 1
