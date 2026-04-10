"""Task state management with SQLite write-back cache.

Public API (unchanged):
    set_task(task_id, data)   — create/replace a task
    update_task(task_id, **kw) — partial update
    get_task(task_id)          — get task dict (copy)
    get_active_tasks()         — list non-terminal tasks

Lifecycle (new):
    init_task_store()     — call at startup
    shutdown_task_store()  — call at shutdown
    clear_tasks()          — reset everything (tests)
"""

import logging
import os
import threading
import time
from typing import Any

from app.task_db import (
    db_clear,
    db_close,
    db_get,
    db_upsert,
    db_upsert_many,
    db_delete_expired,
    db_get_active,
    init_db,
)

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_tasks: dict[str, dict[str, Any]] = {}
_dirty: set[str] = set()

_flush_thread: threading.Thread | None = None
_stop_event = threading.Event()

_FLUSH_INTERVAL = 2.0  # seconds
_COMPLETED_TTL = float(os.getenv("TASK_TTL_COMPLETED", "3600"))
_ERROR_TTL = float(os.getenv("TASK_TTL_ERROR", "86400"))

# Internal metadata keys filtered from public responses
_META_KEYS = frozenset({"created_at", "updated_at"})


def _strip_meta(data: dict) -> dict:
    """Remove internal metadata keys from a task dict."""
    return {k: v for k, v in data.items() if k not in _META_KEYS}


# ---------------------------------------------------------------------------
# Public API (same signatures as before)
# ---------------------------------------------------------------------------

def set_task(task_id: str, data: dict[str, Any]) -> None:
    """Create or fully replace a task. Immediately persisted to SQLite."""
    now = time.time()
    record = dict(data)
    record.setdefault("created_at", now)
    record["updated_at"] = now
    with _lock:
        _tasks[task_id] = record
        _dirty.discard(task_id)
    # Immediate persist — set_task is called rarely (4 places)
    db_upsert(task_id, record)


def update_task(task_id: str, **kwargs: Any) -> None:
    """Partial update of a task. Hot path — writes to memory only.

    Terminal states (completed/error) are flushed to SQLite immediately
    so they survive a crash right after completion.
    """
    now = time.time()
    flush_now = False
    with _lock:
        if task_id not in _tasks:
            return
        _tasks[task_id].update(kwargs)
        _tasks[task_id]["updated_at"] = now
        status = _tasks[task_id].get("status")
        if status in ("completed", "error"):
            flush_now = True
            _dirty.discard(task_id)
            snapshot = dict(_tasks[task_id])
        else:
            _dirty.add(task_id)

    if flush_now:
        db_upsert(task_id, snapshot)


def get_task(task_id: str) -> dict[str, Any]:
    """Return a copy of a task dict, or {} if not found.

    Checks in-memory cache first, falls back to SQLite (post-restart).
    """
    with _lock:
        data = _tasks.get(task_id)
        if data is not None:
            return _strip_meta(dict(data))
    # Fallback: task may exist in SQLite from a previous run
    row = db_get(task_id)
    if row:
        with _lock:
            _tasks[task_id] = row
        return _strip_meta(dict(row))
    return {}


def get_active_tasks() -> list[dict[str, Any]]:
    """Return all non-terminal tasks with task_id field included."""
    with _lock:
        return [
            {"task_id": tid, **_strip_meta(data)}
            for tid, data in _tasks.items()
            if data.get("status") not in ("completed", "error")
        ]


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

def init_task_store() -> None:
    """Initialise SQLite, recover tasks from previous run, start flush thread."""
    global _flush_thread, _COMPLETED_TTL, _ERROR_TTL

    # Re-read env (tests may override)
    _COMPLETED_TTL = float(os.getenv("TASK_TTL_COMPLETED", "3600"))
    _ERROR_TTL = float(os.getenv("TASK_TTL_ERROR", "86400"))

    init_db()

    # Recover active tasks from SQLite
    recovered = db_get_active()
    with _lock:
        _tasks.clear()
        _dirty.clear()
        for row in recovered:
            tid = row["task_id"]
            # In-flight tasks cannot resume (temp files are gone)
            if row.get("status") in ("downloading", "uploading", "downloading_from_remote"):
                row["status"] = "error"
                row["error"] = "interrupted by restart"
                row["updated_at"] = time.time()
                db_upsert(tid, row)
                logger.info("Task %s marked as error (interrupted by restart)", tid)
            _tasks[tid] = row

    if recovered:
        logger.info("Recovered %d task(s) from SQLite", len(recovered))

    # Start flush thread
    _stop_event.clear()
    _flush_thread = threading.Thread(target=_flush_loop, daemon=True, name="task-flush")
    _flush_thread.start()


def shutdown_task_store() -> None:
    """Final flush and close DB."""
    _stop_event.set()
    if _flush_thread is not None:
        _flush_thread.join(timeout=5)
    _do_flush()
    db_close()


def clear_tasks() -> None:
    """Reset all state — memory and SQLite. For tests."""
    with _lock:
        _tasks.clear()
        _dirty.clear()
    db_clear()


# ---------------------------------------------------------------------------
# Background flush
# ---------------------------------------------------------------------------

def _do_flush() -> None:
    """Flush dirty tasks to SQLite and run TTL cleanup."""
    # 1. Batch-write dirty tasks
    with _lock:
        if _dirty:
            to_flush = {tid: dict(_tasks[tid]) for tid in _dirty if tid in _tasks}
            _dirty.clear()
        else:
            to_flush = {}

    if to_flush:
        db_upsert_many(to_flush)

    # 2. TTL cleanup
    deleted = db_delete_expired(_COMPLETED_TTL, _ERROR_TTL)
    if deleted:
        # Also evict from memory
        cutoff_completed = time.time() - _COMPLETED_TTL
        cutoff_error = time.time() - _ERROR_TTL
        with _lock:
            expired_ids = [
                tid for tid, data in _tasks.items()
                if (data.get("status") == "completed" and data.get("updated_at", 0) < cutoff_completed)
                or (data.get("status") == "error" and data.get("updated_at", 0) < cutoff_error)
            ]
            for tid in expired_ids:
                del _tasks[tid]
        if expired_ids:
            logger.info("TTL cleanup: removed %d expired task(s)", len(expired_ids))


def _flush_loop() -> None:
    """Background thread: flush dirty tasks every _FLUSH_INTERVAL seconds."""
    while not _stop_event.is_set():
        _stop_event.wait(timeout=_FLUSH_INTERVAL)
        if _stop_event.is_set():
            break
        try:
            _do_flush()
        except Exception:
            logger.exception("Error in task flush loop")
