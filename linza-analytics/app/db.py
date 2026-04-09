import sqlite3
import os
import time

import app.config as config

DEFAULT_CONFIG = [
    ("NUDE", "18+"),
    ("SEX", "18+"),
    ("KIDSPORN", "prohibited"),
    ("ALCOHOL", "16+"),
    ("SMOKING", "16+"),
    ("DRUGS", "prohibited"),
    ("DRUGS2KIDS", "prohibited"),
    ("VANDALISM", "16+"),
    ("VIOLENCE", "16+"),
    ("SUICIDE", "prohibited"),
    ("KIDSSUICIDE", "prohibited"),
    ("OBSCENE_LANGUAGE", "16+"),
    ("TERROR", "prohibited"),
    ("EXTREMISM", "prohibited"),
    ("TERRORCONTENT", "prohibited"),
    ("LGBT", "prohibited"),
    ("CHILDFREE", "18+"),
    ("INOAGENT", "18+"),
    ("INOAGENTCONTENT", "18+"),
    ("ANTIWAR", "18+"),
    ("LUDOMANIA", "18+"),
]


def _get_conn():
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS classifier_config (
                subclass TEXT PRIMARY KEY,
                category TEXT NOT NULL CHECK(category IN ('prohibited', '18+', '16+'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS classifier_audit (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                request_id   TEXT NOT NULL DEFAULT '',
                action       TEXT NOT NULL CHECK(action IN ('update', 'reset')),
                subclass     TEXT NOT NULL,
                old_category TEXT NOT NULL CHECK(old_category IN ('prohibited', '18+', '16+')),
                new_category TEXT NOT NULL CHECK(new_category IN ('prohibited', '18+', '16+'))
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM classifier_config").fetchone()[0]
        if count == 0:
            _seed_defaults(conn)


def _seed_defaults(conn, *, request_id: str | None = None):
    """Seed default config. Must be called inside `with conn:` context manager
    which handles BEGIN/COMMIT/ROLLBACK automatically."""
    # Read current state BEFORE delete (for audit diff)
    old_state = {}
    if request_id is not None:
        old_state = {
            r["subclass"]: r["category"]
            for r in conn.execute("SELECT subclass, category FROM classifier_config").fetchall()
        }
    conn.execute("DELETE FROM classifier_config")
    conn.executemany(
        "INSERT INTO classifier_config (subclass, category) VALUES (?, ?)",
        DEFAULT_CONFIG,
    )
    # Audit: log only actual changes
    if request_id is not None:
        default_map = dict(DEFAULT_CONFIG)
        changes = [
            (request_id, sub, old_state[sub], default_map[sub])
            for sub in old_state
            if old_state[sub] != default_map.get(sub)
        ]
        if changes:
            conn.executemany(
                "INSERT INTO classifier_audit (request_id, action, subclass, old_category, new_category) "
                "VALUES (?, 'reset', ?, ?, ?)",
                changes,
            )


def get_all():
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT subclass, category FROM classifier_config ORDER BY subclass"
        ).fetchall()
        return [{"subclass": r["subclass"], "category": r["category"]} for r in rows]


def update_all(items: list, *, request_id: str | None = None):
    with _get_conn() as conn:
        # Deduplicate: last value wins (matches ON CONFLICT DO UPDATE behaviour)
        final = {item["subclass"]: item["category"] for item in items}

        # Read current state for audit diff
        if request_id is not None:
            placeholders = ",".join("?" * len(final))
            old_state = {
                r["subclass"]: r["category"]
                for r in conn.execute(
                    f"SELECT subclass, category FROM classifier_config WHERE subclass IN ({placeholders})",
                    list(final.keys()),
                ).fetchall()
            }

        conn.executemany(
            """
            INSERT INTO classifier_config (subclass, category) VALUES (?, ?)
            ON CONFLICT(subclass) DO UPDATE SET category = excluded.category
            """,
            [(sub, cat) for sub, cat in final.items()],
        )

        # Audit: log only actual changes
        if request_id is not None:
            changes = [
                (request_id, sub, old_state[sub], final[sub])
                for sub in final
                if old_state.get(sub) is not None and old_state[sub] != final[sub]
            ]
            if changes:
                conn.executemany(
                    "INSERT INTO classifier_audit (request_id, action, subclass, old_category, new_category) "
                    "VALUES (?, 'update', ?, ?, ?)",
                    changes,
                )


def seed_defaults(*, request_id: str | None = None):
    with _get_conn() as conn:
        _seed_defaults(conn, request_id=request_id)


def get_audit(*, subclass: str | None = None, action: str | None = None,
              limit: int = 50, offset: int = 0) -> list[dict]:
    """Query the classifier audit log with optional filters."""
    with _get_conn() as conn:
        query = "SELECT id, timestamp, request_id, action, subclass, old_category, new_category FROM classifier_audit"
        conditions: list[str] = []
        params: list = []
        if subclass:
            conditions.append("subclass = ?")
            params.append(subclass)
        if action:
            conditions.append("action = ?")
            params.append(action)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
