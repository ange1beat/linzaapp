"""API-level tests for classifier audit log endpoint (analytics#10)."""


class TestAuditViaUpdate:
    """PUT /api/classifier/ creates audit entries visible at GET /api/classifier/audit."""

    def test_update_creates_audit_via_api(self, client):
        client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": "prohibited"},
        ])
        resp = client.get("/api/classifier/audit")
        assert resp.status_code == 200
        rows = resp.json()
        assert len(rows) == 1
        assert rows[0]["subclass"] == "NUDE"
        assert rows[0]["old_category"] == "18+"
        assert rows[0]["new_category"] == "prohibited"
        assert rows[0]["action"] == "update"

    def test_update_no_change_empty_audit(self, client):
        """PUT with current value produces no audit."""
        client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": "18+"},
        ])
        resp = client.get("/api/classifier/audit")
        assert resp.status_code == 200
        assert resp.json() == []


class TestAuditViaReset:
    def test_reset_creates_audit_via_api(self, client):
        # Change something first
        client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": "prohibited"},
        ])
        # Reset
        client.put("/api/classifier/reset")
        resp = client.get("/api/classifier/audit")
        rows = resp.json()
        # At least one reset entry (NUDE back to 18+)
        reset_rows = [r for r in rows if r["action"] == "reset"]
        assert len(reset_rows) >= 1
        nude_reset = [r for r in reset_rows if r["subclass"] == "NUDE"]
        assert len(nude_reset) == 1
        assert nude_reset[0]["old_category"] == "prohibited"
        assert nude_reset[0]["new_category"] == "18+"


class TestAuditRequestId:
    def test_audit_contains_provided_request_id(self, client):
        client.put(
            "/api/classifier/",
            json=[{"subclass": "NUDE", "category": "prohibited"}],
            headers={"X-Request-ID": "test-req-42"},
        )
        rows = client.get("/api/classifier/audit").json()
        assert len(rows) == 1
        assert rows[0]["request_id"] == "test-req-42"

    def test_audit_has_generated_request_id(self, client):
        """Without X-Request-ID header, middleware generates an 8-char ID."""
        client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": "prohibited"},
        ])
        rows = client.get("/api/classifier/audit").json()
        assert len(rows) == 1
        assert len(rows[0]["request_id"]) == 8


class TestAuditFilters:
    def _seed_audit(self, client):
        """Create a mix of update and reset audit entries."""
        client.put("/api/classifier/", json=[
            {"subclass": "NUDE", "category": "prohibited"},
            {"subclass": "ALCOHOL", "category": "18+"},
        ])
        client.put("/api/classifier/reset")

    def test_filter_by_subclass(self, client):
        self._seed_audit(client)
        rows = client.get("/api/classifier/audit?subclass=NUDE").json()
        assert all(r["subclass"] == "NUDE" for r in rows)
        assert len(rows) >= 1

    def test_filter_by_action(self, client):
        self._seed_audit(client)
        rows = client.get("/api/classifier/audit?action=reset").json()
        assert all(r["action"] == "reset" for r in rows)
        assert len(rows) >= 1

    def test_pagination(self, client):
        # Create several audit entries
        for cat in ["prohibited", "18+", "prohibited"]:
            client.put("/api/classifier/", json=[
                {"subclass": "NUDE", "category": cat},
            ])
        page1 = client.get("/api/classifier/audit?limit=2&offset=0").json()
        page2 = client.get("/api/classifier/audit?limit=2&offset=2").json()
        assert len(page1) == 2
        assert len(page2) == 1  # 3 total, offset 2 → 1 remaining
        # No overlap
        ids1 = {r["id"] for r in page1}
        ids2 = {r["id"] for r in page2}
        assert ids1.isdisjoint(ids2)


class TestAuditEdgeCases:
    def test_audit_empty_on_fresh_db(self, client):
        resp = client.get("/api/classifier/audit")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_audit_limit_validation(self, client):
        assert client.get("/api/classifier/audit?limit=0").status_code == 422
        assert client.get("/api/classifier/audit?limit=501").status_code == 422

    def test_get_classifier_no_audit_entry(self, client):
        """GET (read-only) must not create audit entries."""
        client.get("/api/classifier/")
        rows = client.get("/api/classifier/audit").json()
        assert rows == []
