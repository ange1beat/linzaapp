"""Tests for S3 failure scenarios — ClientError, connection issues, partial failures."""

from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError


def _client_error(code: str, message: str = "error"):
    return ClientError(
        {"Error": {"Code": code, "Message": message}},
        "TestOperation",
    )


class TestDownloadS3Failures:
    """S3 failures in download endpoint (files.py:561-568)."""

    def test_head_object_not_found(self, client):
        mock_s3 = MagicMock()
        mock_s3.head_object.side_effect = _client_error("404", "Not Found")
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = client.get("/api/files/download/uploads/missing.mp4")
        assert resp.status_code == 404

    def test_head_object_access_denied(self, client):
        mock_s3 = MagicMock()
        mock_s3.head_object.side_effect = _client_error("403", "Access Denied")
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = client.get("/api/files/download/uploads/secret.mp4")
        # Any S3 error on head_object → 404 (file not found from client perspective)
        assert resp.status_code == 404


class TestDeleteS3Failures:
    """S3 failures in delete endpoint (files.py:537-558)."""

    def test_partial_delete_failure(self, client):
        """Some keys delete successfully, some fail."""
        mock_s3 = MagicMock()
        call_count = [0]

        def _delete_side_effect(**kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise _client_error("InternalError", "S3 hiccup")

        mock_s3.delete_object.side_effect = _delete_side_effect
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = client.post("/api/files/delete-objects", json={
                "keys": ["uploads/a.mp4", "uploads/b.mp4", "uploads/c.mp4"]
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2  # 2 succeeded
        assert len(data["errors"]) == 1  # 1 failed
        assert data["errors"][0]["key"] == "uploads/b.mp4"

    def test_all_deletes_fail(self, client):
        mock_s3 = MagicMock()
        mock_s3.delete_object.side_effect = _client_error("AccessDenied", "No perms")
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = client.post("/api/files/delete-objects", json={
                "keys": ["uploads/x.mp4"]
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert len(data["errors"]) == 1


class TestListS3Failures:
    """S3 failures in list endpoint (files.py:360-375)."""

    def test_list_with_sources_prefix(self, client):
        """Files with sources/ prefix should appear in from_sources."""
        mock_s3 = MagicMock()
        from datetime import datetime, timezone
        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "uploads/a.mp4", "Size": 100,
                 "LastModified": datetime(2025, 1, 1, tzinfo=timezone.utc)},
                {"Key": "sources/remote/b.mp4", "Size": 200,
                 "LastModified": datetime(2025, 1, 1, tzinfo=timezone.utc)},
            ]
        }
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = client.get("/api/files/")
        data = resp.json()
        assert len(data["uploads"]) == 1
        assert len(data["from_sources"]) == 1
        assert data["from_sources"][0]["name"] == "sources/remote/b.mp4"

    def test_list_includes_active_tasks(self, client):
        """Active tasks should appear in response alongside files."""
        from app.tasks import set_task
        set_task("test-task", {"status": "downloading", "filename": "uploads/new.mp4",
                               "progress": 50, "total": 100})
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {}
        with patch("app.routes.files.get_s3", return_value=mock_s3), \
             patch("app.routes.files.get_bucket", return_value="b"):
            resp = client.get("/api/files/")
        data = resp.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["task_id"] == "test-task"
        assert data["tasks"][0]["status"] == "downloading"
