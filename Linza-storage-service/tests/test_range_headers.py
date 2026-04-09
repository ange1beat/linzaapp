"""Tests for Range header edge cases in download endpoint."""

from io import BytesIO
from unittest.mock import patch, MagicMock


def _mock_s3_with_file(size: int = 1000):
    """Create a mock S3 client with a file of given size."""
    mock_s3 = MagicMock()
    mock_s3.head_object.return_value = {
        "ContentLength": size,
        "ContentType": "video/mp4",
    }
    body = MagicMock()
    body.read.side_effect = [b"x" * min(size, 512 * 1024), b""]
    mock_s3.get_object.return_value = {"Body": body}
    return mock_s3


def _download(client, key="uploads/video.mp4", range_header=None):
    headers = {}
    if range_header is not None:
        headers["Range"] = range_header
    return client.get(f"/api/files/download/{key}", headers=headers)


class TestRangeHeaderValidation:
    """Edge cases for Range header parsing (files.py:584-598)."""

    def test_missing_bytes_prefix(self, client):
        mock_s3 = _mock_s3_with_file()
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = _download(client, range_header="items=0-100")
        assert resp.status_code == 416

    def test_non_numeric_range(self, client):
        mock_s3 = _mock_s3_with_file()
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = _download(client, range_header="bytes=abc-def")
        assert resp.status_code == 416

    def test_start_greater_than_end(self, client):
        mock_s3 = _mock_s3_with_file(1000)
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = _download(client, range_header="bytes=500-100")
        assert resp.status_code == 416

    def test_start_beyond_file_size(self, client):
        mock_s3 = _mock_s3_with_file(1000)
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = _download(client, range_header="bytes=2000-3000")
        assert resp.status_code == 416

    def test_empty_range_value(self, client):
        """bytes= with nothing after should fail."""
        mock_s3 = _mock_s3_with_file(1000)
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = _download(client, range_header="bytes=")
        assert resp.status_code == 416

    def test_valid_range_returns_206(self, client):
        mock_s3 = _mock_s3_with_file(1000)
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = _download(client, range_header="bytes=0-499")
        assert resp.status_code == 206
        assert resp.headers["content-range"] == "bytes 0-499/1000"

    def test_end_clamped_to_file_size(self, client):
        mock_s3 = _mock_s3_with_file(100)
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = _download(client, range_header="bytes=0-999999")
        assert resp.status_code == 206
        assert resp.headers["content-range"] == "bytes 0-99/100"

    def test_no_range_returns_200(self, client):
        mock_s3 = _mock_s3_with_file(100)
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = _download(client)
        assert resp.status_code == 200
        assert "content-range" not in resp.headers
