"""Tests for app.tasks — persistent task state management."""

import time

from app.tasks import (
    set_task,
    update_task,
    get_task,
    get_active_tasks,
    init_task_store,
    _do_flush,
    _tasks,
    _lock,
)


# ---------------------------------------------------------------------------
# Original tests (same behaviour, public API unchanged)
# ---------------------------------------------------------------------------


class TestSetTask:
    def test_creates_task(self):
        set_task("t1", {"status": "pending", "filename": "a.txt"})
        result = get_task("t1")
        assert result["status"] == "pending"
        assert result["filename"] == "a.txt"

    def test_overwrites_existing_task(self):
        set_task("t1", {"status": "pending"})
        set_task("t1", {"status": "downloading", "progress": 50})
        result = get_task("t1")
        assert result["status"] == "downloading"
        assert result["progress"] == 50
        # old keys should be gone (full replace)
        assert "filename" not in result


class TestUpdateTask:
    def test_modifies_fields(self):
        set_task("t1", {"status": "pending", "progress": 0})
        update_task("t1", status="downloading", progress=42)
        result = get_task("t1")
        assert result["status"] == "downloading"
        assert result["progress"] == 42

    def test_noop_for_missing_task(self):
        # Should not raise
        update_task("nonexistent", status="error")
        assert get_task("nonexistent") == {}


class TestGetTask:
    def test_returns_correct_task(self):
        set_task("t1", {"status": "pending"})
        set_task("t2", {"status": "completed"})
        assert get_task("t1")["status"] == "pending"
        assert get_task("t2")["status"] == "completed"

    def test_returns_empty_dict_for_unknown(self):
        assert get_task("unknown") == {}

    def test_returns_copy_not_reference(self):
        set_task("t1", {"status": "pending"})
        result = get_task("t1")
        result["status"] = "hacked"
        assert get_task("t1")["status"] == "pending"


class TestGetActiveTasks:
    def test_filters_completed(self):
        set_task("t1", {"status": "pending"})
        set_task("t2", {"status": "completed"})
        active = get_active_tasks()
        ids = [t["task_id"] for t in active]
        assert "t1" in ids
        assert "t2" not in ids

    def test_filters_error(self):
        set_task("t1", {"status": "downloading"})
        set_task("t2", {"status": "error", "error": "boom"})
        active = get_active_tasks()
        ids = [t["task_id"] for t in active]
        assert "t1" in ids
        assert "t2" not in ids

    def test_empty_when_all_done(self):
        set_task("t1", {"status": "completed"})
        set_task("t2", {"status": "error"})
        assert get_active_tasks() == []

    def test_includes_task_id_field(self):
        set_task("abc", {"status": "uploading", "progress": 10})
        active = get_active_tasks()
        assert len(active) == 1
        assert active[0]["task_id"] == "abc"
        assert active[0]["progress"] == 10


# ---------------------------------------------------------------------------
# New: persistence tests
# ---------------------------------------------------------------------------


class TestPersistence:
    def test_task_survives_reinit(self):
        """Completed task should be readable from SQLite after reinit."""
        set_task("t1", {"status": "completed", "filename": "a.mp4", "progress": 100, "total": 100})
        # Reinit simulates a restart — clears memory, reloads from SQLite
        init_task_store()
        result = get_task("t1")
        assert result["status"] == "completed"
        assert result["filename"] == "a.mp4"

    def test_active_task_marked_error_on_reinit(self):
        """An in-flight task should be marked as error after restart."""
        set_task("t1", {"status": "downloading", "filename": "b.mp4", "progress": 50, "total": 100})
        init_task_store()
        result = get_task("t1")
        assert result["status"] == "error"
        assert "interrupted" in result.get("error", "")

    def test_uploading_task_marked_error_on_reinit(self):
        """Uploading task should also be marked as error after restart."""
        set_task("t1", {"status": "uploading", "filename": "c.mp4"})
        init_task_store()
        assert get_task("t1")["status"] == "error"

    def test_pending_task_stays_pending_on_reinit(self):
        """Pending task should survive restart unchanged."""
        set_task("t1", {"status": "pending", "filename": "d.mp4"})
        init_task_store()
        assert get_task("t1")["status"] == "pending"

    def test_dirty_task_flushed_and_recovered(self):
        """A task updated via update_task (dirty) should be recoverable after flush + reinit."""
        set_task("t1", {"status": "pending", "filename": "e.mp4", "progress": 0, "total": 1000})
        update_task("t1", status="downloading", progress=500)
        _do_flush()  # simulate background flush
        init_task_store()
        result = get_task("t1")
        # downloading → error on reinit
        assert result["status"] == "error"
        assert result["progress"] == 500

    def test_metadata_not_in_response(self):
        """created_at and updated_at should not appear in get_task() output."""
        set_task("t1", {"status": "pending", "filename": "f.mp4"})
        result = get_task("t1")
        assert "created_at" not in result
        assert "updated_at" not in result

    def test_metadata_not_in_active_tasks(self):
        """created_at and updated_at should not appear in get_active_tasks() output."""
        set_task("t1", {"status": "pending", "filename": "g.mp4"})
        active = get_active_tasks()
        assert len(active) == 1
        assert "created_at" not in active[0]
        assert "updated_at" not in active[0]


class TestTTLCleanup:
    def test_ttl_removes_old_completed(self, monkeypatch):
        """Completed tasks older than TTL should be cleaned up."""
        monkeypatch.setenv("TASK_TTL_COMPLETED", "10")
        init_task_store()
        set_task("t1", {"status": "completed", "filename": "old.mp4"})
        # Backdate updated_at to make it expired
        with _lock:
            _tasks["t1"]["updated_at"] = time.time() - 20
        from app.task_db import db_upsert
        with _lock:
            db_upsert("t1", _tasks["t1"])
        _do_flush()
        assert get_task("t1") == {}

    def test_ttl_preserves_recent_completed(self, monkeypatch):
        """Recent completed tasks should NOT be cleaned up."""
        monkeypatch.setenv("TASK_TTL_COMPLETED", "3600")
        init_task_store()
        set_task("t1", {"status": "completed", "filename": "recent.mp4"})
        _do_flush()
        assert get_task("t1")["status"] == "completed"

    def test_ttl_removes_old_error(self, monkeypatch):
        """Error tasks older than TTL should be cleaned up."""
        monkeypatch.setenv("TASK_TTL_ERROR", "10")
        init_task_store()
        set_task("t1", {"status": "error", "error": "fail", "filename": "err.mp4"})
        with _lock:
            _tasks["t1"]["updated_at"] = time.time() - 20
        from app.task_db import db_upsert
        with _lock:
            db_upsert("t1", _tasks["t1"])
        _do_flush()
        assert get_task("t1") == {}
