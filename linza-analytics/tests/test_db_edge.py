"""Edge case tests for database layer — init, seeding, concurrent access."""

import threading

from app.db import get_all, init_db, seed_defaults, update_all


class TestInitDbEdgeCases:

    def test_init_idempotent(self):
        """Calling init_db() multiple times doesn't duplicate data."""
        init_db()
        init_db()
        items = get_all()
        assert len(items) == 21

    def test_init_skips_seeding_when_data_exists(self):
        """If table already has data, init_db() does not re-seed."""
        update_all([{"subclass": "NUDE", "category": "prohibited"}])
        init_db()  # should NOT reset
        nude = next(i for i in get_all() if i["subclass"] == "NUDE")
        assert nude["category"] == "prohibited"


class TestUpdateAllEdgeCases:

    def test_empty_list_is_noop(self):
        before = get_all()
        update_all([])
        after = get_all()
        assert before == after

    def test_update_single_item(self):
        update_all([{"subclass": "NUDE", "category": "prohibited"}])
        nude = next(i for i in get_all() if i["subclass"] == "NUDE")
        assert nude["category"] == "prohibited"

    def test_update_all_21_items(self):
        items = [{"subclass": i["subclass"], "category": "prohibited"} for i in get_all()]
        update_all(items)
        result = get_all()
        assert all(i["category"] == "prohibited" for i in result)


class TestSeedDefaultsEdgeCases:

    def test_seed_restores_all_defaults(self):
        update_all([{"subclass": "NUDE", "category": "prohibited"}])
        seed_defaults()
        nude = next(i for i in get_all() if i["subclass"] == "NUDE")
        assert nude["category"] == "18+"

    def test_seed_idempotent(self):
        seed_defaults()
        first = get_all()
        seed_defaults()
        second = get_all()
        assert first == second


class TestConcurrentAccess:
    """SQLite WAL mode should handle concurrent reads/writes."""

    def test_concurrent_reads(self):
        results = [None] * 5
        errors = []

        def read(idx):
            try:
                results[idx] = get_all()
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=read, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors
        for r in results:
            assert len(r) == 21

    def test_concurrent_writes(self):
        errors = []

        def write(category):
            try:
                update_all([{"subclass": "NUDE", "category": category}])
            except Exception as exc:
                errors.append(exc)

        categories = ["prohibited", "18+", "16+", "prohibited", "18+"]
        threads = [threading.Thread(target=write, args=(c,)) for i, c in enumerate(categories)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors
        nude = next(i for i in get_all() if i["subclass"] == "NUDE")
        assert nude["category"] in {"prohibited", "18+", "16+"}
