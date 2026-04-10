def test_login_correct_credentials(client):
    response = client.post("/api/auth/login", json={
        "login": "admin",
        "password": "admin",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post("/api/auth/login", json={
        "login": "admin",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_me_with_valid_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["login"] == "admin"
    assert data["role"] == "superadmin"
    assert data["first_name"] == "Super"
    assert data["last_name"] == "Admin"
    assert data["email"] == "admin@linza.local"
    assert isinstance(data.get("portal_roles"), list)
    assert len(data["portal_roles"]) >= 1
    assert data.get("active_role") in data["portal_roles"]


def test_switch_role(client, auth_headers):
    r = client.post(
        "/api/auth/switch-role",
        headers=auth_headers,
        json={"active_role": "lawyer"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["active_role"] == "lawyer"


def test_me_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_login_rate_limit_exceeded(client):
    """Brute-force protection: 6th attempt in a minute returns 429."""
    for _ in range(5):
        client.post("/api/auth/login", json={"login": "admin", "password": "wrong"})
    resp = client.post("/api/auth/login", json={"login": "admin", "password": "wrong"})
    assert resp.status_code == 429


def test_login_succeeds_within_limit(client):
    """Valid login within rate limit still succeeds."""
    for _ in range(4):
        client.post("/api/auth/login", json={"login": "admin", "password": "wrong"})
    resp = client.post("/api/auth/login", json={"login": "admin", "password": "admin"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
