"""Integration tests for /api/settings/sources endpoints (board#28)."""


SOURCE_DATA = {
    "name": "Test Source",
    "path_type": "http",
    "path_url": "https://cdn.example.com/videos/",
    "file_extensions": "mp4,avi",
    "priority": "High",
    "workspace": "Test WS",
}


def test_list_sources_requires_auth(client):
    resp = client.get("/api/settings/sources/")
    assert resp.status_code == 401


def test_list_sources_empty(client, auth_headers):
    resp = client.get("/api/settings/sources/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_source(client, auth_headers):
    resp = client.post("/api/settings/sources/", json=SOURCE_DATA, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Source"
    assert "id" in data


def test_update_source(client, auth_headers):
    create = client.post("/api/settings/sources/", json=SOURCE_DATA, headers=auth_headers)
    sid = create.json()["id"]

    resp = client.put(f"/api/settings/sources/{sid}", json={
        **SOURCE_DATA, "name": "Renamed",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"


def test_update_source_not_found(client, auth_headers):
    resp = client.put("/api/settings/sources/99999", json=SOURCE_DATA, headers=auth_headers)
    assert resp.status_code == 404


def test_delete_source(client, auth_headers):
    create = client.post("/api/settings/sources/", json=SOURCE_DATA, headers=auth_headers)
    sid = create.json()["id"]

    resp = client.delete(f"/api/settings/sources/{sid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"


def test_delete_source_not_found(client, auth_headers):
    resp = client.delete("/api/settings/sources/99999", headers=auth_headers)
    assert resp.status_code == 404
