"""Tests for remote S3 operations — list and import endpoints."""

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone


REMOTE_CREDS = {
    "endpoint_url": "https://s3.remote.example.com",
    "bucket_name": "remote-bucket",
    "access_key_id": "REMOTE_KEY",
    "secret_access_key": "REMOTE_SECRET",
    "region": "us-east-1",
}


class TestRemoteS3List:
    """POST /api/files/remote-s3/list (files.py:457-488)."""

    def test_list_returns_objects(self, client):
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "data/video1.mp4", "Size": 1024,
                 "LastModified": datetime(2025, 6, 1, tzinfo=timezone.utc)},
                {"Key": "data/video2.mp4", "Size": 2048,
                 "LastModified": datetime(2025, 7, 1, tzinfo=timezone.utc)},
            ],
            "IsTruncated": False,
        }
        with patch("app.routes.files._remote_s3_client", return_value=mock_client):
            resp = client.post("/api/files/remote-s3/list", json={
                **REMOTE_CREDS,
                "prefix": "data/",
                "max_keys": 100,
            })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["objects"]) == 2
        assert data["objects"][0]["key"] == "data/video1.mp4"
        assert data["objects"][0]["size"] == 1024
        assert data["is_truncated"] is False

    def test_list_empty_bucket(self, client):
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {"IsTruncated": False}
        with patch("app.routes.files._remote_s3_client", return_value=mock_client):
            resp = client.post("/api/files/remote-s3/list", json=REMOTE_CREDS)
        assert resp.status_code == 200
        assert resp.json()["objects"] == []

    def test_list_connection_error(self, client):
        mock_client = MagicMock()
        mock_client.list_objects_v2.side_effect = Exception("Connection refused")
        with patch("app.routes.files._remote_s3_client", return_value=mock_client):
            resp = client.post("/api/files/remote-s3/list", json=REMOTE_CREDS)
        assert resp.status_code == 502
        assert "Не удалось прочитать" in resp.json()["detail"]

    def test_list_max_keys_validation(self, client):
        """max_keys must be between 1 and 1000."""
        resp = client.post("/api/files/remote-s3/list", json={
            **REMOTE_CREDS, "max_keys": 0,
        })
        assert resp.status_code == 422

        resp = client.post("/api/files/remote-s3/list", json={
            **REMOTE_CREDS, "max_keys": 1001,
        })
        assert resp.status_code == 422


class TestRemoteS3Import:
    """POST /api/files/remote-s3/import (files.py:491-514)."""

    def test_import_returns_task_and_dest_keys(self, client):
        with patch("app.routes.files._import_remote_s3_task"):
            resp = client.post("/api/files/remote-s3/import", json={
                **REMOTE_CREDS,
                "keys": ["videos/clip1.mp4", "videos/clip2.mp4"],
            })
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert len(data["keys"]) == 2
        # source_import_storage_key strips leading slashes and adds sources/ prefix
        assert all(k.startswith("sources/") for k in data["keys"])

    def test_import_empty_keys_returns_422(self, client):
        resp = client.post("/api/files/remote-s3/import", json={
            **REMOTE_CREDS,
            "keys": [],
        })
        assert resp.status_code == 422

    def test_import_missing_credentials_returns_422(self, client):
        resp = client.post("/api/files/remote-s3/import", json={
            "keys": ["file.mp4"],
        })
        assert resp.status_code == 422
