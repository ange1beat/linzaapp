"""Tests for AccessCredential password encryption."""

import os

from cryptography.fernet import Fernet


def _ensure_encryption_key():
    """Ensure a stable encryption key exists for tests."""
    if not os.environ.get("CREDENTIAL_ENCRYPTION_KEY"):
        os.environ["CREDENTIAL_ENCRYPTION_KEY"] = Fernet.generate_key().decode()


_ensure_encryption_key()

from backend.encryption import encrypt_password, decrypt_password, _FERNET_PREFIX


# ---------------------------------------------------------------------------
# Unit tests for encrypt/decrypt functions
# ---------------------------------------------------------------------------

def test_encrypt_returns_prefixed_ciphertext():
    ct = encrypt_password("secret123")
    assert ct.startswith(_FERNET_PREFIX)
    assert "secret123" not in ct


def test_decrypt_roundtrip():
    ct = encrypt_password("my-password")
    assert decrypt_password(ct) == "my-password"


def test_decrypt_legacy_plaintext():
    """Legacy plaintext values (no prefix) are returned as-is."""
    assert decrypt_password("old-plaintext-pass") == "old-plaintext-pass"


def test_encrypt_empty_string():
    assert encrypt_password("") == ""
    assert decrypt_password("") == ""


# ---------------------------------------------------------------------------
# API integration tests
# ---------------------------------------------------------------------------

def test_create_credential_stores_encrypted(client, auth_headers, db_session):
    """POST /api/settings/access/ stores password as Fernet ciphertext."""
    resp = client.post("/api/settings/access/", json={
        "name": "test-cred",
        "login": "user1",
        "password": "super-secret",
    }, headers=auth_headers)
    assert resp.status_code == 200
    cred_id = resp.json()["id"]

    # Read directly from DB — password must be encrypted, not plaintext
    from backend.models import AccessCredential
    cred = db_session.query(AccessCredential).filter_by(id=cred_id).first()
    assert cred is not None
    assert cred.password_encrypted.startswith(_FERNET_PREFIX)
    assert "super-secret" not in cred.password_encrypted

    # Decrypt should recover original
    assert decrypt_password(cred.password_encrypted) == "super-secret"


def test_update_credential_encrypts_password(client, auth_headers, db_session):
    """PUT /api/settings/access/{id} encrypts updated password."""
    resp = client.post("/api/settings/access/", json={
        "name": "cred-to-update",
        "password": "initial-pass",
    }, headers=auth_headers)
    cred_id = resp.json()["id"]

    client.put(f"/api/settings/access/{cred_id}", json={
        "name": "cred-to-update",
        "password": "new-pass",
    }, headers=auth_headers)

    from backend.models import AccessCredential
    cred = db_session.query(AccessCredential).filter_by(id=cred_id).first()
    assert cred.password_encrypted.startswith(_FERNET_PREFIX)
    assert decrypt_password(cred.password_encrypted) == "new-pass"


def test_list_credentials_never_exposes_password(client, auth_headers):
    """GET /api/settings/access/ must never include password in response."""
    client.post("/api/settings/access/", json={
        "name": "hidden-pass-cred",
        "password": "do-not-expose",
    }, headers=auth_headers)

    resp = client.get("/api/settings/access/", headers=auth_headers)
    assert resp.status_code == 200
    for cred in resp.json():
        assert "password" not in cred
        assert "password_encrypted" not in cred
        assert "do-not-expose" not in str(cred)


def test_startup_migrates_plaintext_to_encrypted(db_session):
    """Plaintext passwords in DB are migrated to Fernet on startup."""
    from backend.models import AccessCredential
    from backend.main import _migrate_plaintext_credentials

    # Insert a credential with plaintext password directly
    cred = AccessCredential(name="legacy", password_encrypted="old-plain")
    db_session.add(cred)
    db_session.commit()
    db_session.refresh(cred)

    _migrate_plaintext_credentials(db_session)
    db_session.refresh(cred)

    assert cred.password_encrypted.startswith(_FERNET_PREFIX)
    assert decrypt_password(cred.password_encrypted) == "old-plain"
