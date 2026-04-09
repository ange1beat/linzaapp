"""Edge case tests for classifier API — validation, boundaries, partial updates."""

from app.db import DEFAULT_CONFIG


class TestPutValidationEdgeCases:
    """PUT /api/classifier/ — input validation edge cases."""

    def test_empty_list_is_noop(self, client):
        before = client.get("/api/classifier/").json()
        resp = client.put("/api/classifier/", json=[])
        assert resp.status_code == 200
        assert resp.json() == before

    def test_exactly_100_items_accepted(self, client):
        """Boundary: 100 items should succeed (limit is >100)."""
        items = [{"subclass": "NUDE", "category": "18+"}] * 100
        resp = client.put("/api/classifier/", json=items)
        assert resp.status_code == 200

    def test_101_items_rejected(self, client):
        items = [{"subclass": "NUDE", "category": "18+"}] * 101
        resp = client.put("/api/classifier/", json=items)
        assert resp.status_code == 400
        assert "Too many" in resp.json()["detail"]

    def test_lowercase_subclass_rejected(self, client):
        resp = client.put("/api/classifier/", json=[
            {"subclass": "nude", "category": "18+"},
        ])
        assert resp.status_code == 400
        assert "Unknown subclass" in resp.json()["detail"]

    def test_empty_subclass_rejected(self, client):
        """Field(min_length=1) should reject empty string."""
        resp = client.put("/api/classifier/", json=[
            {"subclass": "", "category": "18+"},
        ])
        assert resp.status_code == 422

    def test_long_subclass_rejected(self, client):
        """Field(max_length=50) should reject strings > 50 chars."""
        resp = client.put("/api/classifier/", json=[
            {"subclass": "A" * 51, "category": "18+"},
        ])
        assert resp.status_code == 422

    def test_empty_category_rejected(self, client):
        resp = client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": ""},
        ])
        assert resp.status_code == 400
        assert "Invalid category" in resp.json()["detail"]

    def test_missing_category_field_rejected(self, client):
        resp = client.put("/api/classifier/", json=[{"subclass": "NUDE"}])
        assert resp.status_code == 422

    def test_missing_subclass_field_rejected(self, client):
        resp = client.put("/api/classifier/", json=[{"category": "18+"}])
        assert resp.status_code == 422

    def test_not_a_list_rejected(self, client):
        resp = client.put("/api/classifier/", json={"subclass": "NUDE", "category": "18+"})
        assert resp.status_code == 422

    def test_duplicate_subclasses_last_wins(self, client):
        """Two updates to same subclass in one request — last value persists."""
        resp = client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": "prohibited"},
            {"subclass": "NUDE", "category": "16+"},
        ])
        assert resp.status_code == 200
        items = resp.json()
        nude = next(i for i in items if i["subclass"] == "NUDE")
        assert nude["category"] == "16+"


class TestPartialUpdate:
    """PUT updates subset of items, others stay unchanged."""

    def test_partial_update_preserves_others(self, client):
        # Update only NUDE
        client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": "prohibited"},
        ])
        items = client.get("/api/classifier/").json()
        nude = next(i for i in items if i["subclass"] == "NUDE")
        alcohol = next(i for i in items if i["subclass"] == "ALCOHOL")
        assert nude["category"] == "prohibited"
        assert alcohol["category"] == "16+"  # unchanged default

    def test_multiple_sequential_updates(self, client):
        client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": "prohibited"},
        ])
        client.put("/api/classifier/", json=[
            {"subclass": "ALCOHOL", "category": "prohibited"},
        ])
        items = client.get("/api/classifier/").json()
        nude = next(i for i in items if i["subclass"] == "NUDE")
        alcohol = next(i for i in items if i["subclass"] == "ALCOHOL")
        assert nude["category"] == "prohibited"
        assert alcohol["category"] == "prohibited"


class TestResetEdgeCases:
    """PUT /api/classifier/reset edge cases."""

    def test_reset_after_multiple_updates(self, client):
        """All 21 items restored to defaults after arbitrary updates."""
        client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": "prohibited"},
            {"subclass": "ALCOHOL", "category": "prohibited"},
            {"subclass": "TERROR", "category": "16+"},
        ])
        resp = client.put("/api/classifier/reset")
        items = resp.json()
        assert len(items) == 21
        defaults = {s: c for s, c in DEFAULT_CONFIG}
        for item in items:
            assert item["category"] == defaults[item["subclass"]]

    def test_reset_idempotent(self, client):
        first = client.put("/api/classifier/reset").json()
        second = client.put("/api/classifier/reset").json()
        assert first == second


class TestGetResponse:
    """GET /api/classifier/ response format."""

    def test_returns_exactly_21_items(self, client):
        items = client.get("/api/classifier/").json()
        assert len(items) == 21

    def test_sorted_alphabetically(self, client):
        items = client.get("/api/classifier/").json()
        subclasses = [i["subclass"] for i in items]
        assert subclasses == sorted(subclasses)

    def test_each_item_has_only_two_fields(self, client):
        items = client.get("/api/classifier/").json()
        for item in items:
            assert set(item.keys()) == {"subclass", "category"}

    def test_all_categories_valid(self, client):
        items = client.get("/api/classifier/").json()
        valid = {"prohibited", "18+", "16+"}
        for item in items:
            assert item["category"] in valid
