"""Tests for /api/files endpoints."""

from datetime import datetime, timezone
from unittest.mock import patch, MagicMock


class TestListFiles:
    def test_returns_files_from_s3(self, client):
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {
                    "Key": "video.mp4",
                    "Size": 1024,
                    "LastModified": datetime(2025, 1, 1, tzinfo=timezone.utc),
                },
                {
                    "Key": "image.png",
                    "Size": 512,
                    "LastModified": datetime(2025, 6, 15, tzinfo=timezone.utc),
                },
            ]
        }

        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="test-bucket"):
            resp = client.get("/api/files/")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["files"]) == 2
        assert len(data["uploads"]) == 2
        assert data["from_sources"] == []
        assert data["files"][0]["name"] == "video.mp4"
        assert data["files"][0]["size"] == 1024
        assert data["files"][1]["name"] == "image.png"
        mock_s3.list_objects_v2.assert_called_once_with(Bucket="test-bucket")

    def test_returns_empty_on_s3_error(self, client):
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.side_effect = Exception("connection refused")

        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="test-bucket"):
            resp = client.get("/api/files/")

        assert resp.status_code == 200
        data = resp.json()
        assert data["files"] == []

    def test_returns_empty_when_bucket_empty(self, client):
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {}

        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="test-bucket"):
            resp = client.get("/api/files/")

        assert resp.status_code == 200
        assert resp.json()["files"] == []


class TestUploadFromUrl:
    def test_empty_url_returns_400(self, client):
        resp = client.post("/api/files/upload-from-url", json={"url": ""})
        assert resp.status_code == 400

    def test_whitespace_url_returns_400(self, client):
        resp = client.post("/api/files/upload-from-url", json={"url": "   "})
        assert resp.status_code == 400

    def test_missing_url_returns_422(self, client):
        resp = client.post("/api/files/upload-from-url", json={})
        assert resp.status_code == 422

    def test_valid_url_returns_task(self, client):
        with patch("app.routes.files._upload_task"):
            resp = client.post("/api/files/upload-from-url", json={
                "url": "https://example.com/data/report.pdf"
            })
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert data["filename"] == "uploads/report.pdf"


class TestHeadDownload:
    """HEAD /api/files/download/{key} — для VPleer до потоковой отдачи."""

    def test_head_returns_200_and_headers(self, client):
        mock_s3 = MagicMock()
        mock_s3.head_object.return_value = {
            "ContentLength": 1234567,
            "ContentType": "application/octet-stream",
        }
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="test-bucket"):
            resp = client.head("/api/files/download/uploads/movie.mov")

        assert resp.status_code == 200
        assert resp.content == b""
        assert resp.headers.get("accept-ranges") == "bytes"
        assert resp.headers.get("content-length") == "1234567"
        assert resp.headers.get("content-type") == "video/quicktime"
        mock_s3.head_object.assert_called_once_with(Bucket="test-bucket", Key="uploads/movie.mov")

    def test_head_unknown_key_404(self, client):
        mock_s3 = MagicMock()
        mock_s3.head_object.side_effect = Exception("NoSuchKey")
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="test-bucket"):
            resp = client.head("/api/files/download/missing.bin")
        assert resp.status_code == 404
