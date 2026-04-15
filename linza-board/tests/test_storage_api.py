"""Integration tests for /api/settings/storage endpoints (board#28)."""


PROFILE_DATA = {
    "name": "Test Source",
    "profile_type": "source",
    "s3_endpoint_url": "https://s3.example.com",
    "s3_access_key_id": "AKIAEXAMPLE12345678",
    "s3_secret_access_key": "secret123",
    "s3_bucket_name": "test-bucket",
    "s3_region": "us-east-1",
}


def test_list_profiles_requires_auth(client):
    resp = client.get("/api/settings/storage/")
    assert resp.status_code == 401


def test_list_profiles_empty(client, auth_headers):
    resp = client.get("/api/settings/storage/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_profile(client, auth_headers):
    resp = client.post("/api/settings/storage/", json=PROFILE_DATA, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Source"
    assert data["profile_type"] == "source"
    assert "AKIAEXAM..." == data["s3_access_key_id"]  # masked


def test_create_profile_invalid_type(client, auth_headers):
    bad = {**PROFILE_DATA, "profile_type": "invalid"}
    resp = client.post("/api/settings/storage/", json=bad, headers=auth_headers)
    assert resp.status_code == 400


def test_update_profile(client, auth_headers):
    create = client.post("/api/settings/storage/", json=PROFILE_DATA, headers=auth_headers)
    pid = create.json()["id"]

    resp = client.put(f"/api/settings/storage/{pid}", json={
        "name": "Updated Name",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"


def test_update_profile_not_found(client, auth_headers):
    resp = client.put("/api/settings/storage/99999", json={"name": "x"}, headers=auth_headers)
    assert resp.status_code == 404


def test_delete_profile(client, auth_headers):
    create = client.post("/api/settings/storage/", json=PROFILE_DATA, headers=auth_headers)
    pid = create.json()["id"]

    resp = client.delete(f"/api/settings/storage/{pid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"


def test_delete_active_profile_fails(client, auth_headers):
    """Cannot delete an active profile."""
    create = client.post("/api/settings/storage/", json=PROFILE_DATA, headers=auth_headers)
    pid = create.json()["id"]
    client.post(f"/api/settings/storage/{pid}/activate", headers=auth_headers)

    resp = client.delete(f"/api/settings/storage/{pid}", headers=auth_headers)
    assert resp.status_code == 400


def test_activate_profile(client, auth_headers):
    create = client.post("/api/settings/storage/", json=PROFILE_DATA, headers=auth_headers)
    pid = create.json()["id"]

    resp = client.post(f"/api/settings/storage/{pid}/activate", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is True


def test_activate_deactivates_others(client, auth_headers):
    """Activating one profile deactivates others of same type."""
    p1 = client.post("/api/settings/storage/", json=PROFILE_DATA, headers=auth_headers).json()
    p2 = client.post("/api/settings/storage/", json={**PROFILE_DATA, "name": "Second"}, headers=auth_headers).json()

    client.post(f"/api/settings/storage/{p1['id']}/activate", headers=auth_headers)
    client.post(f"/api/settings/storage/{p2['id']}/activate", headers=auth_headers)

    profiles = client.get("/api/settings/storage/", headers=auth_headers).json()
    active = [p for p in profiles if p["is_active"]]
    assert len(active) == 1
    assert active[0]["id"] == p2["id"]
