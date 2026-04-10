def test_list_users_requires_auth(client):
    response = client.get("/api/users/")
    assert response.status_code == 401


def test_list_users_as_admin(client, auth_headers):
    response = client.get("/api/users/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At least the seeded superadmin should exist
    assert len(data) >= 1
    logins = [u["login"] for u in data]
    assert "admin" in logins


def test_create_user(client, auth_headers):
    response = client.post("/api/users/", headers=auth_headers, json={
        "first_name": "Test",
        "last_name": "User",
        "login": "testuser",
        "password": "testpassword123",
        "email": "test@example.com",
        "role": "user",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["login"] == "testuser"
    assert data["role"] == "user"
    assert data["first_name"] == "Test"
    assert data["email"] == "test@example.com"


def test_delete_user(client, auth_headers):
    # First create a user to delete
    create_resp = client.post("/api/users/", headers=auth_headers, json={
        "first_name": "ToDelete",
        "last_name": "User",
        "login": "deleteuser",
        "password": "password123",
        "email": "delete@example.com",
        "role": "user",
    })
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    # Delete the user
    delete_resp = client.delete(f"/api/users/{user_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    # Verify user is gone
    list_resp = client.get("/api/users/", headers=auth_headers)
    logins = [u["login"] for u in list_resp.json()]
    assert "deleteuser" not in logins
