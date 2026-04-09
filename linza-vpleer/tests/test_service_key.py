"""Tests for X-Service-Key middleware."""

from unittest.mock import patch


class TestServiceKeyMiddleware:

    def test_health_open_without_key(self, client):
        with patch("app.main.SERVICE_API_KEY", "test-secret"):
            resp = client.get("/health")
        assert resp.status_code == 200

    def test_rejected_without_key(self, client):
        with patch("app.main.SERVICE_API_KEY", "test-secret"):
            resp = client.get("/api/vpleer/files")
        assert resp.status_code == 401

    def test_rejected_wrong_key(self, client):
        with patch("app.main.SERVICE_API_KEY", "test-secret"):
            resp = client.get("/api/vpleer/files", headers={"X-Service-Key": "wrong"})
        assert resp.status_code == 401

    def test_accepted_with_correct_key(self, client):
        with patch("app.main.SERVICE_API_KEY", "test-secret"):
            resp = client.get("/api/vpleer/files", headers={"X-Service-Key": "test-secret"})
        # May return 502 if storage is unavailable, but NOT 401
        assert resp.status_code != 401

    def test_no_key_configured_passes_all(self, client):
        with patch("app.main.SERVICE_API_KEY", ""):
            resp = client.get("/api/vpleer/files")
        assert resp.status_code != 401
