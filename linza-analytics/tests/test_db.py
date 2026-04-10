import sqlite3

import app.db as db_module
from app.db import DEFAULT_CONFIG, get_all, init_db, seed_defaults, update_all


def test_init_db_creates_table_and_seeds(tmp_db):
    """init_db (called by the autouse fixture) creates the table and seeds 21 rows."""
    conn = sqlite3.connect(tmp_db, timeout=10)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM classifier_config").fetchall()
    conn.close()
    assert len(rows) == 21


def test_get_all_returns_sorted_items(tmp_db):
    items = get_all()
    assert len(items) == 21
    subclasses = [item["subclass"] for item in items]
    assert subclasses == sorted(subclasses)


def test_update_all_updates_records(tmp_db):
    update_all([{"subclass": "NUDE", "category": "prohibited"}])
    items = get_all()
    nude = next(item for item in items if item["subclass"] == "NUDE")
    assert nude["category"] == "prohibited"


def test_seed_defaults_resets_to_defaults(tmp_db):
    # Change a record first
    update_all([{"subclass": "NUDE", "category": "prohibited"}])
    # Reset
    seed_defaults()
    items = get_all()
    nude = next(item for item in items if item["subclass"] == "NUDE")
    assert nude["category"] == "18+"
    assert len(items) == 21
