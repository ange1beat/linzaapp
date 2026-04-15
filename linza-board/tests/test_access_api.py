"""Integration tests for /api/settings/access endpoints (board#28)."""


CRED_DATA = {
    "name": "Test Credential",
    "domain": "example.com",
    "login": "testuser",
    "password": "secret123",
    "workspace": "Test WS",
}


def test_list_credentials_requires_auth(client):
    resp = client.get("/api/settings/access/")
    assert resp.status_code == 401


def test_list_credentials_empty(client, auth_headers):
    resp = client.get("/api/settings/access/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_credential(client, auth_headers):
    resp = client.post("/api/settings/access/", json=CRED_DATA, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Credential"
    assert "id" in data


def test_list_credentials_hides_password(client, auth_headers):
    """Password is NOT returned in list response."""
    client.post("/api/settings/access/", json=CRED_DATA, headers=auth_headers)
    resp = client.get("/api/settings/access/", headers=auth_headers)
    creds = resp.json()
    assert len(creds) >= 1
    assert "password" not in creds[0]
    assert "password_encrypted" not in creds[0]


def test_update_credential(client, auth_headers):
    create = client.post("/api/settings/access/", json=CRED_DATA, headers=auth_headers)
    cid = create.json()["id"]

    resp = client.put(f"/api/settings/access/{cid}", json={
        **CRED_DATA, "name": "Updated Cred",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Cred"


def test_update_credential_not_found(client, auth_headers):
    resp = client.put("/api/settings/access/99999", json=CRED_DATA, headers=auth_headers)
    assert resp.status_code == 404


def test_delete_credential(client, auth_headers):
    create = client.post("/api/settings/access/", json=CRED_DATA, headers=auth_headers)
    cid = create.json()["id"]

    resp = client.delete(f"/api/settings/access/{cid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"


def test_delete_credential_not_found(client, auth_headers):
    resp = client.delete("/api/settings/access/99999", headers=auth_headers)
    assert resp.status_code == 404
