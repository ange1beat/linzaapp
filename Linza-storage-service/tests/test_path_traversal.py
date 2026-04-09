"""Tests for S3 key validation — path traversal, prefix enforcement."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest


class TestDownloadValidation:
    """GET /api/files/download/{filename} — validate_s3_key() guard."""

    def test_rejects_bare_traversal(self, client):
        resp = client.get("/api/files/download/%2e%2e/etc/passwd")
        assert resp.status_code == 400

    def test_rejects_uploads_traversal(self, client):
        resp = client.get("/api/files/download/uploads/../secret.txt")
        assert resp.status_code == 400

    def test_rejects_no_prefix(self, client):
        resp = client.get("/api/files/download/secret.txt")
        assert resp.status_code == 400

    def test_rejects_absolute_path(self, client):
        resp = client.get("/api/files/download/%2Fetc%2Fpasswd")
        assert resp.status_code == 400

    def test_accepts_valid_uploads_key(self, client):
        mock_s3 = MagicMock()
        mock_s3.head_object.return_value = {
            "ContentLength": 4,
            "ContentType": "video/mp4",
        }
        body = MagicMock()
        body.read.side_effect = [b"data", b""]
        body.close = MagicMock()
        mock_s3.get_object.return_value = {"Body": body}

        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="test-bucket"):
            resp = client.get("/api/files/download/uploads/video.mp4")
        assert resp.status_code == 200

    def test_accepts_valid_sources_key(self, client):
        mock_s3 = MagicMock()
        mock_s3.head_object.return_value = {
            "ContentLength": 2,
            "ContentType": "application/json",
        }
        body = MagicMock()
        body.read.side_effect = [b"{}", b""]
        body.close = MagicMock()
        mock_s3.get_object.return_value = {"Body": body}

        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="test-bucket"):
            resp = client.get("/api/files/download/sources/data.json")
        assert resp.status_code == 200


class TestDeleteValidation:
    """POST /api/files/delete-objects — only_managed_prefixes() guard."""

    def test_filters_traversal_keys(self, client):
        """All keys contain traversal → validator rejects with 422."""
        resp = client.post(
            "/api/files/delete-objects",
            json={"keys": ["uploads/../secret.txt"]},
        )
        assert resp.status_code == 422

    def test_accepts_valid_keys(self, client):
        mock_s3 = MagicMock()
        mock_s3.delete_objects.return_value = {
            "Deleted": [{"Key": "uploads/a.mp4"}, {"Key": "sources/b.json"}],
        }
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="test-bucket"):
            resp = client.post(
                "/api/files/delete-objects",
                json={"keys": ["uploads/a.mp4", "sources/b.json"]},
            )
        assert resp.status_code == 200
        assert resp.json()["count"] == 2
