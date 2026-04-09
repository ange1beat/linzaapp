"""Tests for /api/config endpoints."""

from unittest.mock import patch


class TestGetS3Config:
    def test_returns_masked_config(self, client):
        with patch("app.routes.config.get_config", return_value={
            "endpoint_url": "https://s3.example.com",
            "access_key_id": "ABCD1234...",
            "bucket_name": "test-bucket",
            "region": "us-east-1",
        }):
            resp = client.get("/api/config/s3")
        assert resp.status_code == 200
        data = resp.json()
        assert data["bucket_name"] == "test-bucket"
        assert data["region"] == "us-east-1"
        assert data["endpoint_url"] == "https://s3.example.com"
        assert "access_key_id" in data

    def test_returns_200(self, client):
        resp = client.get("/api/config/s3")
        assert resp.status_code == 200


class TestPutS3Config:
    def test_updates_config(self, client):
        with patch("app.routes.config.reconfigure") as mock_reconf, \
             patch("app.routes.config.get_config", return_value={
                 "endpoint_url": "https://new-s3.example.com",
                 "access_key_id": "NEWKEY1...",
                 "bucket_name": "new-bucket",
                 "region": "eu-west-1",
             }):
            resp = client.put("/api/config/s3", json={
                "endpoint_url": "https://new-s3.example.com",
                "bucket_name": "new-bucket",
                "region": "eu-west-1",
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["config"]["bucket_name"] == "new-bucket"
        mock_reconf.assert_called_once()

    def test_partial_update(self, client):
        with patch("app.routes.config.reconfigure") as mock_reconf, \
             patch("app.routes.config.get_config", return_value={
                 "endpoint_url": "https://s3.cloud.ru",
                 "access_key_id": "OLD...",
                 "bucket_name": "updated-bucket",
                 "region": "ru-central-1",
             }):
            resp = client.put("/api/config/s3", json={
                "bucket_name": "updated-bucket",
            })
        assert resp.status_code == 200
        call_kwargs = mock_reconf.call_args
        assert call_kwargs.kwargs.get("bucket_name") == "updated-bucket" or \
               call_kwargs[1].get("bucket_name") == "updated-bucket"
