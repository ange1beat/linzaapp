"""Tests for upload edge cases — local upload, URL parsing, content types."""

import io
from unittest.mock import patch, MagicMock


class TestUploadLocal:
    """POST /api/files/upload-local (files.py:430-454)."""

    def test_upload_local_returns_task(self, client, tmp_path, monkeypatch):
        monkeypatch.setattr("app.routes.files.TEMP_DIR", str(tmp_path))
        with patch("app.routes.files._upload_from_path_task"):
            resp = client.post(
                "/api/files/upload-local",
                files={"file": ("test.mp4", io.BytesIO(b"fake-video-data"), "video/mp4")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert data["filename"] == "uploads/test.mp4"

    def test_upload_local_with_name_generates_key(self, client, tmp_path, monkeypatch):
        monkeypatch.setattr("app.routes.files.TEMP_DIR", str(tmp_path))
        with patch("app.routes.files._upload_from_path_task"):
            resp = client.post(
                "/api/files/upload-local",
                files={"file": ("report.pdf", io.BytesIO(b"data"), "application/pdf")},
            )
        assert resp.status_code == 200
        assert resp.json()["filename"] == "uploads/report.pdf"

    def test_upload_local_missing_file_returns_422(self, client):
        resp = client.post("/api/files/upload-local")
        assert resp.status_code == 422


class TestUploadFromUrlEdgeCases:
    """Edge cases for POST /api/files/upload-from-url (files.py:409-427)."""

    def test_url_with_query_params_extracts_filename(self, client):
        with patch("app.routes.files._upload_task"):
            resp = client.post("/api/files/upload-from-url", json={
                "url": "https://cdn.example.com/media/clip.mp4?token=abc&expires=123"
            })
        assert resp.status_code == 200
        assert resp.json()["filename"] == "uploads/clip.mp4"

    def test_url_with_encoded_filename(self, client):
        with patch("app.routes.files._upload_task"):
            resp = client.post("/api/files/upload-from-url", json={
                "url": "https://example.com/files/%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE.mp4"
            })
        assert resp.status_code == 200
        assert resp.json()["filename"] == "uploads/видео.mp4"

    def test_url_without_path_generates_filename(self, client):
        with patch("app.routes.files._upload_task"):
            resp = client.post("/api/files/upload-from-url", json={
                "url": "https://example.com/"
            })
        assert resp.status_code == 200
        # Should generate fallback filename
        assert resp.json()["filename"].startswith("uploads/file_")

    def test_url_with_trailing_slash(self, client):
        with patch("app.routes.files._upload_task"):
            resp = client.post("/api/files/upload-from-url", json={
                "url": "https://example.com/path/"
            })
        assert resp.status_code == 200
        assert resp.json()["filename"].startswith("uploads/file_")


class TestDownloadContentType:
    """Content-Type detection for video files (files.py:573-582)."""

    def test_mp4_content_type(self, client):
        mock_s3 = MagicMock()
        mock_s3.head_object.return_value = {
            "ContentLength": 100,
            "ContentType": "application/octet-stream",
        }
        body = MagicMock()
        body.read.side_effect = [b"x" * 100, b""]
        mock_s3.get_object.return_value = {"Body": body}
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = client.get("/api/files/download/uploads/test.mp4")
        assert resp.headers["content-type"] == "video/mp4"

    def test_avi_content_type(self, client):
        mock_s3 = MagicMock()
        mock_s3.head_object.return_value = {
            "ContentLength": 100,
            "ContentType": "application/octet-stream",
        }
        body = MagicMock()
        body.read.side_effect = [b"x" * 100, b""]
        mock_s3.get_object.return_value = {"Body": body}
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = client.get("/api/files/download/uploads/test.avi")
        assert resp.headers["content-type"] == "video/x-msvideo"
