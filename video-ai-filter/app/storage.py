import json
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing import Any

_conn_lock = threading.Lock()


def _migrate_jobs_columns(conn: sqlite3.Connection) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(jobs)").fetchall()}
    if "video_fps" not in existing:
        conn.execute("ALTER TABLE jobs ADD COLUMN video_fps REAL")
    if "video_frame_count" not in existing:
        conn.execute("ALTER TABLE jobs ADD COLUMN video_frame_count INTEGER")
    if "categories_json" not in existing:
        conn.execute("ALTER TABLE jobs ADD COLUMN categories_json TEXT")
    if "audio_results_json" not in existing:
        conn.execute("ALTER TABLE jobs ADD COLUMN audio_results_json TEXT")
    if "linza_selection_json" not in existing:
        conn.execute("ALTER TABLE jobs ADD COLUMN linza_selection_json TEXT")
    if "processing_phase" not in existing:
        conn.execute("ALTER TABLE jobs ADD COLUMN processing_phase TEXT")
    if "phase_progress" not in existing:
        conn.execute("ALTER TABLE jobs ADD COLUMN phase_progress REAL")


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    with _conn_lock:
        conn = _connect(db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    video_path TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    error TEXT,
                    frames_total INTEGER,
                    frames_done INTEGER NOT NULL DEFAULT 0,
                    cancelled INTEGER NOT NULL DEFAULT 0,
                    max_frames INTEGER,
                    max_duration_sec REAL,
                    results_json TEXT,
                    video_fps REAL,
                    video_frame_count INTEGER,
                    categories_json TEXT,
                    audio_results_json TEXT,
                    linza_selection_json TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            _migrate_jobs_columns(conn)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    config_json TEXT NOT NULL DEFAULT '{}',
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()


class JobStorage:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return _connect(self._db_path)

    def create_job(
        self,
        video_path: str,
        prompt: str,
        frames_total: int | None,
        max_frames: int | None,
        max_duration_sec: float | None,
        job_id: str | None = None,
        categories_json: str | None = None,
        linza_selection_json: str | None = None,
    ) -> str:
        job_id = job_id or str(uuid.uuid4())
        now = time.time()
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute(
                    """
                    INSERT INTO jobs (
                        id, status, video_path, prompt, error, frames_total, frames_done,
                        cancelled, max_frames, max_duration_sec, results_json,
                        video_fps, video_frame_count, categories_json, audio_results_json,
                        linza_selection_json,
                        created_at, updated_at
                    ) VALUES (?, 'queued', ?, ?, NULL, ?, 0, 0, ?, ?, NULL, NULL, NULL, ?, NULL, ?, ?, ?)
                    """,
                    (
                        job_id,
                        video_path,
                        prompt,
                        frames_total,
                        max_frames,
                        max_duration_sec,
                        categories_json,
                        linza_selection_json,
                        now,
                        now,
                    ),
                )
                conn.commit()
            finally:
                conn.close()
        return job_id

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with _conn_lock:
            conn = self._conn()
            try:
                row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
                if row is None:
                    return None
                return dict(row)
            finally:
                conn.close()

    def set_status(
        self,
        job_id: str,
        status: str,
        *,
        error: str | None = None,
        frames_total: int | None = None,
        frames_done: int | None = None,
    ) -> None:
        now = time.time()
        with _conn_lock:
            conn = self._conn()
            try:
                parts = ["status = ?", "updated_at = ?"]
                values: list[Any] = [status, now]
                if error is not None:
                    parts.append("error = ?")
                    values.append(error)
                if frames_total is not None:
                    parts.append("frames_total = ?")
                    values.append(frames_total)
                if frames_done is not None:
                    parts.append("frames_done = ?")
                    values.append(frames_done)
                values.append(job_id)
                conn.execute(
                    f"UPDATE jobs SET {', '.join(parts)} WHERE id = ?",
                    values,
                )
                conn.commit()
            finally:
                conn.close()

    def increment_frames_done(self, job_id: str, done: int) -> None:
        now = time.time()
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute(
                    "UPDATE jobs SET frames_done = ?, updated_at = ? WHERE id = ?",
                    (done, now, job_id),
                )
                conn.commit()
            finally:
                conn.close()

    def set_processing_phase(self, job_id: str, phase: str, progress: float) -> None:
        """Этап подготовки (например normalize): progress 0..1 для UI."""
        now = time.time()
        p = min(1.0, max(0.0, float(progress)))
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute(
                    """
                    UPDATE jobs SET processing_phase = ?, phase_progress = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (phase, p, now, job_id),
                )
                conn.commit()
            finally:
                conn.close()

    def clear_processing_phase(self, job_id: str) -> None:
        now = time.time()
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute(
                    """
                    UPDATE jobs SET processing_phase = NULL, phase_progress = NULL, updated_at = ?
                    WHERE id = ?
                    """,
                    (now, job_id),
                )
                conn.commit()
            finally:
                conn.close()

    def set_video_metadata(
        self,
        job_id: str,
        *,
        video_fps: float | None,
        video_frame_count: int | None,
    ) -> None:
        now = time.time()
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute(
                    """
                    UPDATE jobs SET video_fps = ?, video_frame_count = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (video_fps, video_frame_count, now, job_id),
                )
                conn.commit()
            finally:
                conn.close()

    def set_audio_results(self, job_id: str, payload_json: str) -> None:
        now = time.time()
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute(
                    "UPDATE jobs SET audio_results_json = ?, updated_at = ? WHERE id = ?",
                    (payload_json, now, job_id),
                )
                conn.commit()
            finally:
                conn.close()

    def append_result(self, job_id: str, results: list[dict[str, Any]]) -> None:
        now = time.time()
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute(
                    "UPDATE jobs SET results_json = ?, updated_at = ? WHERE id = ?",
                    (json.dumps(results), now, job_id),
                )
                conn.commit()
            finally:
                conn.close()

    def set_cancelled(self, job_id: str) -> None:
        now = time.time()
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute(
                    "UPDATE jobs SET cancelled = 1, updated_at = ? WHERE id = ?",
                    (now, job_id),
                )
                conn.commit()
            finally:
                conn.close()

    def is_cancelled(self, job_id: str) -> bool:
        row = self.get_job(job_id)
        return bool(row and row.get("cancelled"))

    def delete_job_record(self, job_id: str) -> None:
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
                conn.commit()
            finally:
                conn.close()

    def get_runtime_config_json(self) -> str | None:
        with _conn_lock:
            conn = self._conn()
            try:
                row = conn.execute(
                    "SELECT config_json FROM runtime_config WHERE id = 1",
                ).fetchone()
                if row is None:
                    return None
                return str(row[0]) if row[0] is not None else None
            finally:
                conn.close()

    def set_runtime_config_json(self, config_json: str) -> None:
        now = time.time()
        with _conn_lock:
            conn = self._conn()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO runtime_config (id, config_json, updated_at) VALUES (1, ?, ?)",
                    (config_json, now),
                )
                conn.commit()
            finally:
                conn.close()
