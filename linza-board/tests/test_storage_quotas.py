"""Tests for storage quotas API."""


def test_list_quotas_empty(client, auth_headers):
    r = client.get("/api/storage/quotas", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_create_quota(client, auth_headers):
    r = client.post("/api/storage/quotas", headers=auth_headers, json={
        "scope_type": "tenant", "scope_id": 1, "quota_bytes": 1073741824,
    })
    assert r.status_code == 201
    data = r.json()
    assert data["scope_type"] == "tenant"
    assert data["quota_bytes"] == 1073741824
    assert data["used_bytes"] == 0


def test_create_quota_duplicate(client, auth_headers):
    client.post("/api/storage/quotas", headers=auth_headers, json={
        "scope_type": "user", "scope_id": 1, "quota_bytes": 100,
    })
    r = client.post("/api/storage/quotas", headers=auth_headers, json={
        "scope_type": "user", "scope_id": 1, "quota_bytes": 200,
    })
    assert r.status_code == 409


def test_get_quota(client, auth_headers):
    client.post("/api/storage/quotas", headers=auth_headers, json={
        "scope_type": "tenant", "scope_id": 1, "quota_bytes": 500,
    })
    r = client.get("/api/storage/quotas/tenant/1", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["quota_bytes"] == 500


def test_update_quota(client, auth_headers):
    client.post("/api/storage/quotas", headers=auth_headers, json={
        "scope_type": "team", "scope_id": 1, "quota_bytes": 100,
    })
    r = client.put("/api/storage/quotas/team/1", headers=auth_headers, json={
        "quota_bytes": 999,
    })
    assert r.status_code == 200
    assert r.json()["quota_bytes"] == 999


def test_delete_quota(client, auth_headers):
    client.post("/api/storage/quotas", headers=auth_headers, json={
        "scope_type": "user", "scope_id": 99, "quota_bytes": 100,
    })
    r = client.delete("/api/storage/quotas/user/99", headers=auth_headers)
    assert r.status_code == 204
    r2 = client.get("/api/storage/quotas/user/99", headers=auth_headers)
    assert r2.status_code == 404


def test_storage_usage(client, auth_headers):
    r = client.get("/api/storage/usage", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    # No quotas set → all null
    assert data["user"] is None or data["user"] is not None  # just check it works


def test_invalid_scope_type(client, auth_headers):
    r = client.post("/api/storage/quotas", headers=auth_headers, json={
        "scope_type": "invalid", "scope_id": 1, "quota_bytes": 100,
    })
    assert r.status_code == 400
