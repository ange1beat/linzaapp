"""Tests for projects CRUD, members, sharing, and favorites."""


def test_create_project(client, auth_headers):
    r = client.post("/api/projects/", headers=auth_headers, json={"name": "Test Project"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Test Project"
    assert data["tenant_id"] == 1


def test_list_projects(client, auth_headers):
    client.post("/api/projects/", headers=auth_headers, json={"name": "P1"})
    client.post("/api/projects/", headers=auth_headers, json={"name": "P2"})
    r = client.get("/api/projects/", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 2
    assert len(data["projects"]) >= 2


def test_get_project(client, auth_headers):
    create = client.post("/api/projects/", headers=auth_headers, json={"name": "Detail"})
    pid = create.json()["id"]
    r = client.get(f"/api/projects/{pid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Detail"


def test_update_project(client, auth_headers):
    create = client.post("/api/projects/", headers=auth_headers, json={"name": "Old"})
    pid = create.json()["id"]
    r = client.patch(f"/api/projects/{pid}", headers=auth_headers, json={"name": "New"})
    assert r.status_code == 200
    assert r.json()["name"] == "New"


def test_delete_project(client, auth_headers):
    create = client.post("/api/projects/", headers=auth_headers, json={"name": "Del"})
    pid = create.json()["id"]
    r = client.delete(f"/api/projects/{pid}", headers=auth_headers)
    assert r.status_code == 204


def test_search_projects(client, auth_headers):
    client.post("/api/projects/", headers=auth_headers, json={"name": "Alpha"})
    client.post("/api/projects/", headers=auth_headers, json={"name": "Beta"})
    r = client.get("/api/projects/?name=Alpha", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["projects"][0]["name"] == "Alpha"


def test_toggle_favorite(client, auth_headers):
    create = client.post("/api/projects/", headers=auth_headers, json={"name": "Fav"})
    pid = create.json()["id"]

    # Add to favorites
    r1 = client.post(f"/api/projects/{pid}/favorite", headers=auth_headers)
    assert r1.status_code == 200
    assert r1.json()["is_favorite"] is True

    # Check favorites list
    favs = client.get("/api/projects/favorites", headers=auth_headers)
    assert any(p["id"] == pid for p in favs.json())

    # Remove from favorites (toggle)
    r2 = client.post(f"/api/projects/{pid}/favorite", headers=auth_headers)
    assert r2.json()["is_favorite"] is False


def test_project_members(client, auth_headers, db_session):
    from backend.models import User
    from backend.auth import hash_password

    user = User(
        first_name="Member", last_name="Test", login="projmember",
        password_hash=hash_password("pass1234"), email="member@test.com",
        role="user", tenant_id=1,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    create = client.post("/api/projects/", headers=auth_headers, json={"name": "WithMembers"})
    pid = create.json()["id"]

    # Add member
    r = client.post(f"/api/projects/{pid}/members", headers=auth_headers, json={
        "user_ids": [user.id], "role": "editor",
    })
    assert r.status_code == 200
    assert r.json()["added"] == 1

    # List members
    members = client.get(f"/api/projects/{pid}/members", headers=auth_headers)
    assert members.status_code == 200
    assert len(members.json()) == 2  # owner (admin) + added user

    # Remove member
    r2 = client.delete(f"/api/projects/{pid}/members/{user.id}", headers=auth_headers)
    assert r2.status_code == 204


def test_project_sharing(client, auth_headers, db_session):
    from backend.models import User, Team
    from backend.auth import hash_password

    create = client.post("/api/projects/", headers=auth_headers, json={"name": "Shared"})
    pid = create.json()["id"]

    # Share with user
    user = User(
        first_name="Share", last_name="Target", login="sharetarget",
        password_hash=hash_password("pass1234"), email="share@test.com",
        role="user", tenant_id=1,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    r = client.post(f"/api/projects/{pid}/share", headers=auth_headers, json={
        "share_type": "user", "share_target_id": user.id, "permission": "view",
    })
    assert r.status_code == 201
    share_id = r.json()["id"]

    # List shares
    shares = client.get(f"/api/projects/{pid}/shares", headers=auth_headers)
    assert len(shares.json()) == 1

    # Revoke share
    r2 = client.delete(f"/api/projects/{pid}/share/{share_id}", headers=auth_headers)
    assert r2.status_code == 204


def test_project_membership_shortcuts(client, auth_headers, db_session):
    from backend.models import User
    from backend.auth import hash_password

    user = User(
        first_name="Bulk", last_name="Member", login="bulkmember",
        password_hash=hash_password("pass1234"), email="bulk@test.com",
        role="user", tenant_id=1,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    p1 = client.post("/api/projects/", headers=auth_headers, json={"name": "P1"}).json()["id"]
    p2 = client.post("/api/projects/", headers=auth_headers, json={"name": "P2"}).json()["id"]

    # Bulk add
    client.patch(f"/api/projects/membership/{user.id}", headers=auth_headers, json={
        "operation": "add", "project_ids": [p1, p2],
    })

    # Check
    r = client.get(f"/api/projects/membership/{user.id}", headers=auth_headers)
    assert set(r.json()["project_ids"]) == {p1, p2}

    # Bulk remove
    client.patch(f"/api/projects/membership/{user.id}", headers=auth_headers, json={
        "operation": "remove", "project_ids": [p1],
    })
    r2 = client.get(f"/api/projects/membership/{user.id}", headers=auth_headers)
    assert r2.json()["project_ids"] == [p2]
