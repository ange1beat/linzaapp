"""Tests for concurrent upload scenarios and task isolation."""

import threading
from unittest.mock import patch

from app.tasks import set_task, update_task, get_task, get_active_tasks


class TestConcurrentTaskUpdates:
    """Verify task isolation under concurrent access."""

    def test_concurrent_updates_dont_corrupt(self):
        """Multiple threads updating different tasks should not interfere."""
        n_tasks = 10
        n_updates = 100

        for i in range(n_tasks):
            set_task(f"task-{i}", {"status": "downloading", "progress": 0, "total": 1000,
                                    "filename": f"uploads/file-{i}.mp4"})

        errors = []

        def _update_loop(task_id: str, target_progress: int):
            try:
                for p in range(target_progress):
                    update_task(task_id, progress=p)
                update_task(task_id, status="completed", progress=target_progress)
            except Exception as exc:
                errors.append(exc)

        threads = []
        for i in range(n_tasks):
            t = threading.Thread(target=_update_loop, args=(f"task-{i}", n_updates))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=5)

        assert not errors, f"Errors during concurrent updates: {errors}"

        # Verify each task has correct final state
        for i in range(n_tasks):
            task = get_task(f"task-{i}")
            assert task["status"] == "completed"
            assert task["progress"] == n_updates

    def test_concurrent_reads_during_writes(self):
        """Reading tasks while they're being updated should return consistent data."""
        set_task("reader-test", {"status": "downloading", "progress": 0,
                                  "total": 1000, "filename": "uploads/test.mp4"})
        read_results = []
        errors = []

        def _writer():
            try:
                for p in range(200):
                    update_task("reader-test", progress=p)
                update_task("reader-test", status="completed", progress=200)
            except Exception as exc:
                errors.append(exc)

        def _reader():
            try:
                for _ in range(200):
                    task = get_task("reader-test")
                    if task:
                        read_results.append(task["progress"])
            except Exception as exc:
                errors.append(exc)

        writer = threading.Thread(target=_writer)
        reader = threading.Thread(target=_reader)
        writer.start()
        reader.start()
        writer.join(timeout=5)
        reader.join(timeout=5)

        assert not errors
        # Progress should be monotonically non-decreasing (no rollbacks)
        for i in range(1, len(read_results)):
            assert read_results[i] >= read_results[i - 1], \
                f"Progress went backwards: {read_results[i-1]} -> {read_results[i]}"


class TestMultipleActiveUploads:
    """Verify multiple uploads tracked independently."""

    def test_multiple_tasks_isolated(self, client):
        """Two concurrent uploads should have independent progress."""
        with patch("app.routes.files._upload_task"):
            resp1 = client.post("/api/files/upload-from-url", json={
                "url": "https://example.com/a.mp4"
            })
            resp2 = client.post("/api/files/upload-from-url", json={
                "url": "https://example.com/b.mp4"
            })

        id1 = resp1.json()["task_id"]
        id2 = resp2.json()["task_id"]
        assert id1 != id2

        # Simulate progress on task 1 only
        update_task(id1, status="downloading", progress=500, total=1000)

        t1 = get_task(id1)
        t2 = get_task(id2)
        assert t1["progress"] == 500
        assert t2["progress"] == 0  # Unchanged
