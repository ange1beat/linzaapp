"""SQLite persistence layer for task state."""

import os
import sqlite3
import threading
import time

_conn: sqlite3.Connection | None = None
_db_lock = threading.Lock()  # Serialize all DB operations on the shared connection

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS tasks (
    task_id     TEXT PRIMARY KEY,
    status      TEXT NOT NULL DEFAULT 'pending',
    filename    TEXT NOT NULL DEFAULT '',
    progress    INTEGER NOT NULL DEFAULT 0,
    total       INTEGER NOT NULL DEFAULT 0,
    batch_index INTEGER,
    batch_total INTEGER,
    error       TEXT,
    created_at  REAL NOT NULL,
    updated_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);
"""

_COLUMNS = (
    "task_id", "status", "filename", "progress", "total",
    "batch_index", "batch_total", "error", "created_at", "updated_at",
)


def init_db(path: str | None = None) -> None:
    """Open (or create) the SQLite database and apply schema."""
    global _conn
    if _conn is not None:
        _conn.close()
    db_path = path or os.getenv("TASK_DB_PATH", "/app/data/tasks.db")
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    _conn = sqlite3.connect(db_path, check_same_thread=False)
    _conn.execute("PRAGMA journal_mode=WAL")
    _conn.execute("PRAGMA synchronous=NORMAL")
    _conn.executescript(_SCHEMA)


def _get_conn() -> sqlite3.Connection:
    if _conn is None:
        raise RuntimeError("task_db not initialised — call init_db() first")
    return _conn


def _row_to_dict(row: tuple) -> dict:
    return {col: val for col, val in zip(_COLUMNS, row) if val is not None}


def db_upsert(task_id: str, data: dict) -> None:
    """Insert or replace a single task."""
    conn = _get_conn()
    now = time.time()
    with _db_lock:
        conn.execute(
            """INSERT OR REPLACE INTO tasks
               (task_id, status, filename, progress, total,
                batch_index, batch_total, error, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task_id,
                data.get("status", "pending"),
                data.get("filename", ""),
                data.get("progress", 0),
                data.get("total", 0),
                data.get("batch_index"),
                data.get("batch_total"),
                data.get("error"),
                data.get("created_at", now),
                data.get("updated_at", now),
            ),
        )
        conn.commit()


def db_upsert_many(tasks: dict[str, dict]) -> None:
    """Batch upsert multiple tasks in a single transaction."""
    if not tasks:
        return
    conn = _get_conn()
    rows = []
    now = time.time()
    for tid, data in tasks.items():
        rows.append((
            tid,
            data.get("status", "pending"),
            data.get("filename", ""),
            data.get("progress", 0),
            data.get("total", 0),
            data.get("batch_index"),
            data.get("batch_total"),
            data.get("error"),
            data.get("created_at", now),
            data.get("updated_at", now),
        ))
    with _db_lock:
        conn.executemany(
            """INSERT OR REPLACE INTO tasks
               (task_id, status, filename, progress, total,
                batch_index, batch_total, error, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        conn.commit()


def db_get(task_id: str) -> dict:
    """Get a single task by ID, or empty dict if not found."""
    conn = _get_conn()
    with _db_lock:
        cur = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cur.fetchone()
    return _row_to_dict(row) if row else {}


def db_get_active() -> list[dict]:
    """Get all tasks not in terminal state."""
    conn = _get_conn()
    with _db_lock:
        cur = conn.execute(
            "SELECT * FROM tasks WHERE status NOT IN ('completed', 'error')"
        )
        rows = cur.fetchall()
    return [_row_to_dict(row) for row in rows]


def db_delete_expired(completed_ttl: float, error_ttl: float) -> int:
    """Delete expired tasks. Returns number of rows deleted."""
    conn = _get_conn()
    now = time.time()
    with _db_lock:
        cur = conn.execute(
            """DELETE FROM tasks
               WHERE (status = 'completed' AND updated_at < ?)
                  OR (status = 'error' AND updated_at < ?)""",
            (now - completed_ttl, now - error_ttl),
        )
        conn.commit()
    return cur.rowcount


def db_clear() -> None:
    """Delete all tasks (for tests)."""
    conn = _get_conn()
    with _db_lock:
        conn.execute("DELETE FROM tasks")
        conn.commit()


def db_close() -> None:
    """Close the database connection."""
    global _conn
    with _db_lock:
        if _conn is not None:
            _conn.close()
            _conn = None
