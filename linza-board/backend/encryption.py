"""Symmetric encryption for sensitive credentials (Fernet / AES-128-CBC).

Usage:
    from backend.encryption import encrypt_password, decrypt_password

    ciphertext = encrypt_password("my-secret")
    plaintext  = decrypt_password(ciphertext)

The encryption key is read from the CREDENTIAL_ENCRYPTION_KEY environment
variable.  If the variable is empty on first startup, a new key is generated
and printed to stdout so the operator can persist it.

Fernet guarantees:
  - AES-128-CBC + HMAC-SHA256 (authenticated encryption)
  - Base64-encoded ciphertext (safe for VARCHAR / TEXT columns)
"""

import os
import logging

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger("linza.encryption")

_FERNET_PREFIX = "fernet:"


def _get_fernet() -> Fernet:
    key = os.getenv("CREDENTIAL_ENCRYPTION_KEY", "")
    if not key:
        key = Fernet.generate_key().decode()
        logger.warning(
            "CREDENTIAL_ENCRYPTION_KEY not set — generated new key: %s  "
            "Persist it in your environment to avoid data loss on restart.",
            key,
        )
        os.environ["CREDENTIAL_ENCRYPTION_KEY"] = key
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_password(plaintext: str) -> str:
    """Encrypt a plaintext password.  Returns prefixed ciphertext."""
    if not plaintext:
        return ""
    f = _get_fernet()
    token = f.encrypt(plaintext.encode()).decode()
    return f"{_FERNET_PREFIX}{token}"


def decrypt_password(stored: str) -> str:
    """Decrypt a stored password.

    Handles both legacy plaintext values (no prefix) and
    Fernet-encrypted values (``fernet:`` prefix).
    """
    if not stored:
        return ""
    if not stored.startswith(_FERNET_PREFIX):
        # Legacy plaintext — return as-is
        return stored
    token = stored[len(_FERNET_PREFIX):]
    f = _get_fernet()
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken:
        logger.error("Failed to decrypt credential — wrong key or corrupted data")
        return ""
