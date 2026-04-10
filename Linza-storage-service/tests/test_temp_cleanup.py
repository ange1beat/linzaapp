"""Tests for orphaned temp file cleanup at startup."""

import os

from app.main import _cleanup_temp_dir, TEMP_DIR


class TestCleanupTempDir:
    def test_removes_orphaned_files(self, tmp_path, monkeypatch):
        temp_dir = str(tmp_path / "linza-storage")
        monkeypatch.setattr("app.main.TEMP_DIR", temp_dir)
        os.makedirs(temp_dir)
        # Create fake orphaned files
        for name in ("storage-abc123.mp4", "storage-def456.bin", "storage-ghi789.tmp"):
            (tmp_path / "linza-storage" / name).write_bytes(b"orphan")

        _cleanup_temp_dir()

        assert os.path.isdir(temp_dir)
        assert os.listdir(temp_dir) == []

    def test_creates_dir_if_missing(self, tmp_path, monkeypatch):
        temp_dir = str(tmp_path / "linza-storage")
        monkeypatch.setattr("app.main.TEMP_DIR", temp_dir)
        assert not os.path.exists(temp_dir)

        _cleanup_temp_dir()

        assert os.path.isdir(temp_dir)

    def test_handles_empty_dir(self, tmp_path, monkeypatch):
        temp_dir = str(tmp_path / "linza-storage")
        monkeypatch.setattr("app.main.TEMP_DIR", temp_dir)
        os.makedirs(temp_dir)

        _cleanup_temp_dir()  # should not raise

        assert os.path.isdir(temp_dir)

    def test_logs_cleanup_count(self, tmp_path, monkeypatch, caplog):
        temp_dir = str(tmp_path / "linza-storage")
        monkeypatch.setattr("app.main.TEMP_DIR", temp_dir)
        os.makedirs(temp_dir)
        for i in range(5):
            (tmp_path / "linza-storage" / f"storage-{i}.tmp").write_bytes(b"x")

        import logging
        with caplog.at_level(logging.INFO, logger="storage-service"):
            _cleanup_temp_dir()

        assert "5 orphaned temp file(s)" in caplog.text

    def test_skips_subdirectories(self, tmp_path, monkeypatch, caplog):
        temp_dir = str(tmp_path / "linza-storage")
        monkeypatch.setattr("app.main.TEMP_DIR", temp_dir)
        os.makedirs(temp_dir)
        subdir = os.path.join(temp_dir, "unexpected-subdir")
        os.makedirs(subdir)
        (tmp_path / "linza-storage" / "storage-file.tmp").write_bytes(b"x")

        import logging
        with caplog.at_level(logging.WARNING, logger="storage-service"):
            _cleanup_temp_dir()

        # File removed, subdir left (with warning)
        assert os.path.isdir(subdir)
        assert not os.path.exists(os.path.join(temp_dir, "storage-file.tmp"))
        assert "Unexpected directory" in caplog.text
