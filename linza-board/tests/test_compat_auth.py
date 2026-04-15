"""Tests for linza-admin compatible auth flow (OTP with stateToken)."""


def test_compat_login_returns_state_token(client):
    """POST /api/auth (compat) → { user, stateToken }."""
    r = client.post("/api/auth", json={"login": "admin", "password": "admin"})
    assert r.status_code == 200
    data = r.json()
    assert "stateToken" in data
    assert "user" in data
    assert data["user"]["email"] == "admin@linza.local"
    assert data["user"]["id"] == "1"  # string, not int


def test_compat_login_wrong_password(client):
    r = client.post("/api/auth", json={"login": "admin", "password": "wrong"})
    assert r.status_code == 401


def test_compat_otp_verify(client):
    """Full OTP flow: login → verify → sign-in."""
    from backend.models import OtpChallenge
    from tests.conftest import TestingSessionLocal

    # Step 1: Login
    login = client.post("/api/auth", json={"login": "admin", "password": "admin"})
    state_token = login.json()["stateToken"]

    # Get the OTP code from DB (in production, it'd be sent via email)
    db = TestingSessionLocal()
    challenge = db.query(OtpChallenge).filter(
        OtpChallenge.state_token == state_token
    ).first()
    assert challenge is not None

    # We need the raw OTP code, but it's hashed. For testing, create a known one.
    from backend.auth import hash_password
    challenge.otp_code = hash_password("123456")
    db.commit()
    db.close()

    # Step 2: Verify OTP
    verify = client.post("/api/auth/factors/otp/verify", json={
        "stateToken": state_token, "passcode": "123456",
    })
    assert verify.status_code == 200
    verify_data = verify.json()
    assert "stateToken" in verify_data
    assert "user" in verify_data

    # Step 3: Sign in
    sign_in = client.post("/api/auth/sign-in", json={
        "stateToken": state_token,
    })
    assert sign_in.status_code == 200
    assert "accessToken" in sign_in.json()  # camelCase!


def test_compat_otp_wrong_code(client):
    login = client.post("/api/auth", json={"login": "admin", "password": "admin"})
    state_token = login.json()["stateToken"]

    verify = client.post("/api/auth/factors/otp/verify", json={
        "stateToken": state_token, "passcode": "000000",
    })
    assert verify.status_code == 401


def test_compat_token_refresh(client, auth_headers):
    """POST /api/auth/token → { accessToken }."""
    r = client.post("/api/auth/token", headers=auth_headers)
    assert r.status_code == 200
    assert "accessToken" in r.json()


def test_compat_sign_out(client, auth_headers):
    r = client.post("/api/auth/sign-out", headers=auth_headers)
    assert r.status_code == 200


def test_compat_otp_resend_email(client):
    login = client.post("/api/auth", json={"login": "admin", "password": "admin"})
    state_token = login.json()["stateToken"]

    r = client.post("/api/auth/factors/otp/challenge/email", json={
        "stateToken": state_token,
    })
    assert r.status_code == 200


def test_compat_otp_resend_sms(client):
    login = client.post("/api/auth", json={"login": "admin", "password": "admin"})
    state_token = login.json()["stateToken"]

    r = client.post("/api/auth/factors/otp/challenge/sms", json={
        "stateToken": state_token,
    })
    assert r.status_code == 200
