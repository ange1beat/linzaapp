"""DB-level tests for classifier audit log (analytics#10)."""

import sqlite3

import app.config as config
from app.db import get_all, get_audit, seed_defaults, update_all


def _raw_audit_count() -> int:
    """Direct SQL count — bypasses get_audit() to verify independently."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    count = conn.execute("SELECT COUNT(*) FROM classifier_audit").fetchone()[0]
    conn.close()
    return count


# ── update_all audit ─────────────────────────────────────────────────────────


def test_update_creates_audit_entry():
    update_all([{"subclass": "NUDE", "category": "prohibited"}], request_id="req-1")
    rows = get_audit()
    assert len(rows) == 1
    assert rows[0]["action"] == "update"
    assert rows[0]["subclass"] == "NUDE"
    assert rows[0]["old_category"] == "18+"
    assert rows[0]["new_category"] == "prohibited"
    assert rows[0]["request_id"] == "req-1"


def test_update_no_change_no_audit():
    """Sending current value should NOT create audit entry."""
    update_all([{"subclass": "NUDE", "category": "18+"}], request_id="req-noop")
    assert _raw_audit_count() == 0


def test_update_without_request_id_no_audit():
    """Backward compat: update_all() without request_id skips audit."""
    update_all([{"subclass": "NUDE", "category": "prohibited"}])
    assert _raw_audit_count() == 0


def test_update_multiple_only_changed_audited():
    """3 items submitted, only 2 actually change — expect 2 audit rows."""
    update_all([
        {"subclass": "NUDE", "category": "prohibited"},   # 18+ → prohibited (change)
        {"subclass": "SEX", "category": "18+"},            # 18+ → 18+ (no change)
        {"subclass": "ALCOHOL", "category": "18+"},        # 16+ → 18+ (change)
    ], request_id="req-multi")
    rows = get_audit()
    assert len(rows) == 2
    subclasses = {r["subclass"] for r in rows}
    assert subclasses == {"NUDE", "ALCOHOL"}
    assert all(r["request_id"] == "req-multi" for r in rows)


# ── seed_defaults (reset) audit ──────────────────────────────────────────────


def test_reset_creates_audit_for_changes():
    """Change 2 items, reset — expect 2 audit rows with action='reset'."""
    update_all([
        {"subclass": "NUDE", "category": "prohibited"},
        {"subclass": "ALCOHOL", "category": "18+"},
    ])  # no request_id → no audit
    seed_defaults(request_id="req-reset")
    rows = get_audit()
    assert len(rows) == 2
    assert all(r["action"] == "reset" for r in rows)
    subclasses = {r["subclass"] for r in rows}
    assert subclasses == {"NUDE", "ALCOHOL"}


def test_reset_no_change_no_audit():
    """Reset when config is already default — no audit entries."""
    seed_defaults(request_id="req-noop-reset")
    assert _raw_audit_count() == 0


def test_reset_without_request_id_no_audit():
    """Backward compat for init_db() path."""
    update_all([{"subclass": "NUDE", "category": "prohibited"}])
    seed_defaults()  # no request_id
    assert _raw_audit_count() == 0


# ── get_audit filtering ─────────────────────────────────────────────────────


def test_get_audit_filters_subclass():
    update_all([
        {"subclass": "NUDE", "category": "prohibited"},
        {"subclass": "ALCOHOL", "category": "18+"},
    ], request_id="req-filter")
    rows = get_audit(subclass="NUDE")
    assert len(rows) == 1
    assert rows[0]["subclass"] == "NUDE"


def test_get_audit_filters_action():
    # Create update entries
    update_all([{"subclass": "NUDE", "category": "prohibited"}], request_id="r1")
    # Create reset entries
    seed_defaults(request_id="r2")

    update_rows = get_audit(action="update")
    reset_rows = get_audit(action="reset")
    assert all(r["action"] == "update" for r in update_rows)
    assert all(r["action"] == "reset" for r in reset_rows)
    assert len(update_rows) >= 1
    assert len(reset_rows) >= 1


def test_get_audit_pagination_and_order():
    """Verify limit/offset and newest-first ordering."""
    for i in range(5):
        update_all(
            [{"subclass": "NUDE", "category": "prohibited" if i % 2 == 0 else "18+"}],
            request_id=f"req-{i}",
        )
    # All 5 updates change NUDE, expect 5 audit rows
    all_rows = get_audit(limit=100)
    assert len(all_rows) == 5
    # Newest first: IDs descending
    assert all_rows[0]["id"] > all_rows[-1]["id"]

    # Pagination
    page1 = get_audit(limit=2, offset=0)
    page2 = get_audit(limit=2, offset=2)
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0]["id"] > page2[0]["id"]
