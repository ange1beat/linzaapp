"""Tests for user profile endpoints (search, me, name, password, etc.)."""


def test_get_me(client, auth_headers):
    r = client.get("/api/users/me", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["first_name"] == "Super"
    assert data["last_name"] == "Admin"
    assert data["tenant_id"] == 1


def test_get_user_by_id(client, auth_headers):
    r = client.get("/api/users/1", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["login"] == "admin"


def test_get_user_not_found(client, auth_headers):
    r = client.get("/api/users/99999", headers=auth_headers)
    assert r.status_code == 404


def test_search_users(client, auth_headers, db_session):
    from backend.models import User
    from backend.auth import hash_password

    for i in range(3):
        db_session.add(User(
            first_name=f"Search{i}", last_name="User", login=f"search{i}",
            password_hash=hash_password("pass1234"), email=f"search{i}@test.com",
            role="user", tenant_id=1,
        ))
    db_session.commit()

    r = client.post("/api/users/search", headers=auth_headers, json={
        "searchTerm": "Search", "pageSize": 10, "pageNumber": 1,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 3
    assert all("Search" in u["first_name"] for u in data["users"])


def test_search_users_pagination(client, auth_headers, db_session):
    from backend.models import User
    from backend.auth import hash_password

    for i in range(5):
        db_session.add(User(
            first_name=f"Page{i}", last_name="Test", login=f"page{i}",
            password_hash=hash_password("pass"), email=f"page{i}@t.com",
            role="user", tenant_id=1,
        ))
    db_session.commit()

    r = client.post("/api/users/search", headers=auth_headers, json={
        "searchTerm": "Page", "pageSize": 2, "pageNumber": 1,
    })
    assert r.status_code == 200
    assert len(r.json()["users"]) == 2
    assert r.json()["total"] >= 5


def test_update_name(client, auth_headers):
    r = client.put("/api/users/me/name", headers=auth_headers, json={
        "firstName": "Updated", "lastName": "Name",
    })
    assert r.status_code == 200
    assert r.json()["first_name"] == "Updated"
    assert r.json()["last_name"] == "Name"


def test_update_password(client, auth_headers):
    r = client.put("/api/users/me/password", headers=auth_headers, json={
        "currentPassword": "admin", "newPassword": "NewPass123!",
    })
    assert r.status_code == 200

    # Verify new password works
    login = client.post("/api/auth/login", json={
        "login": "admin", "password": "NewPass123!",
    })
    assert login.status_code == 200


def test_update_password_wrong_current(client, auth_headers):
    r = client.put("/api/users/me/password", headers=auth_headers, json={
        "currentPassword": "wrongpass", "newPassword": "NewPass123!",
    })
    assert r.status_code == 400


def test_update_telegram(client, auth_headers):
    r = client.put("/api/users/me/telegram", headers=auth_headers, json={
        "username": "@mytelegram",
    })
    assert r.status_code == 200
    assert r.json()["telegram_username"] == "mytelegram"  # stripped @
