"""Tests for teams CRUD and membership API."""


def test_list_teams_empty(client, auth_headers):
    r = client.get("/api/teams/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_create_team(client, auth_headers):
    r = client.post("/api/teams/", headers=auth_headers, json={"name": "Dev Team"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Dev Team"
    assert data["member_count"] == 0


def test_get_team(client, auth_headers):
    create = client.post("/api/teams/", headers=auth_headers, json={"name": "QA"})
    tid = create.json()["id"]
    r = client.get(f"/api/teams/{tid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "QA"


def test_update_team(client, auth_headers):
    create = client.post("/api/teams/", headers=auth_headers, json={"name": "Old"})
    tid = create.json()["id"]
    r = client.patch(f"/api/teams/{tid}", headers=auth_headers, json={"name": "New"})
    assert r.status_code == 200
    assert r.json()["name"] == "New"


def test_delete_team(client, auth_headers):
    create = client.post("/api/teams/", headers=auth_headers, json={"name": "Temp"})
    tid = create.json()["id"]
    r = client.delete(f"/api/teams/{tid}", headers=auth_headers)
    assert r.status_code == 204
    # Verify deleted
    r2 = client.get(f"/api/teams/{tid}", headers=auth_headers)
    assert r2.status_code == 404


def test_team_members_flow(client, auth_headers, db_session):
    """Create team → add member → list → remove."""
    from backend.models import User
    from backend.auth import hash_password

    # Create a regular user
    user = User(
        first_name="Test", last_name="User", login="testmember",
        password_hash=hash_password("pass1234"), email="test@test.com",
        role="user", tenant_id=1,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create team
    team = client.post("/api/teams/", headers=auth_headers, json={"name": "Team A"})
    tid = team.json()["id"]

    # Add member
    r = client.post(f"/api/teams/{tid}/members", headers=auth_headers, json={
        "user_ids": [user.id],
    })
    assert r.status_code == 200
    assert r.json()["updated"] == 1

    # List members
    members = client.get(f"/api/teams/{tid}/members", headers=auth_headers)
    assert members.status_code == 200
    assert len(members.json()) == 1
    assert members.json()[0]["email"] == "test@test.com"

    # Remove member
    r2 = client.delete(f"/api/teams/{tid}/members/{user.id}", headers=auth_headers)
    assert r2.status_code == 204

    # Verify removed
    members2 = client.get(f"/api/teams/{tid}/members", headers=auth_headers)
    assert len(members2.json()) == 0


def test_team_not_found(client, auth_headers):
    r = client.get("/api/teams/99999", headers=auth_headers)
    assert r.status_code == 404
