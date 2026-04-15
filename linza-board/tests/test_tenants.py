"""Tests for tenants CRUD API."""


def test_get_my_tenant(client, auth_headers):
    """Superadmin should have a default tenant."""
    r = client.get("/api/tenants/my", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Default Organization"
    assert data["slug"] == "default"


def test_list_tenants(client, auth_headers):
    r = client.get("/api/tenants/", headers=auth_headers)
    assert r.status_code == 200
    tenants = r.json()
    assert len(tenants) >= 1
    assert tenants[0]["slug"] == "default"


def test_create_tenant(client, auth_headers):
    r = client.post("/api/tenants/", headers=auth_headers, json={
        "name": "Test Company",
        "slug": "test-company",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Test Company"
    assert data["slug"] == "test-company"


def test_create_tenant_duplicate_slug(client, auth_headers):
    client.post("/api/tenants/", headers=auth_headers, json={
        "name": "First", "slug": "dup-slug",
    })
    r = client.post("/api/tenants/", headers=auth_headers, json={
        "name": "Second", "slug": "dup-slug",
    })
    assert r.status_code == 409


def test_update_tenant(client, auth_headers):
    create = client.post("/api/tenants/", headers=auth_headers, json={
        "name": "Old Name",
    })
    tid = create.json()["id"]
    r = client.patch(f"/api/tenants/{tid}", headers=auth_headers, json={
        "name": "New Name",
    })
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


def test_delete_tenant(client, auth_headers):
    create = client.post("/api/tenants/", headers=auth_headers, json={
        "name": "To Delete",
    })
    tid = create.json()["id"]
    r = client.delete(f"/api/tenants/{tid}", headers=auth_headers)
    assert r.status_code == 204


def test_tenant_not_found(client, auth_headers):
    r = client.patch("/api/tenants/99999", headers=auth_headers, json={"name": "X"})
    assert r.status_code == 404
