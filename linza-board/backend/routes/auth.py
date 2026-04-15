import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.requests import Request

from backend.auth import (
    build_token_payload,
    check_credentials,
    create_access_token,
    get_current_user,
    hash_password,
    oauth2_scheme,
    pick_default_active_role,
    portal_roles_for_user,
    resolve_active_role,
    verify_password,
    VALID_PORTAL_ROLES,
)
from backend.database import get_db
from backend.models import OtpChallenge, User
from backend.rate_limit import limiter

router = APIRouter()


def _utcnow():
    """Return current UTC time, timezone-naive for SQLite compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SwitchRoleRequest(BaseModel):
    active_role: str


class MeResponse(BaseModel):
    id: int
    login: str
    role: str
    first_name: str
    last_name: str
    email: str
    phone_number: str | None = None
    telegram_username: str | None = None
    avatar_url: str | None = None
    portal_roles: list[str]
    active_role: str | None = None
    tenant_id: int | None = None
    team_id: int | None = None
    storage_quota_bytes: int = 0
    storage_used_bytes: int = 0


class OtpChallengeRequest(BaseModel):
    email: str
    channel: str = "email"  # "email" | "sms"


class OtpChallengeResponse(BaseModel):
    state_token: str


class OtpVerifyRequest(BaseModel):
    state_token: str
    passcode: str


class OtpVerifyResponse(BaseModel):
    state_token: str
    user: dict


class SignInRequest(BaseModel):
    state_token: str


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------


def _issue_token(user: User, active_role: str | None = None) -> str:
    payload = build_token_payload(user)
    if active_role and active_role in payload["pr"]:
        payload["ar"] = active_role
    return create_access_token(payload)


# ---------------------------------------------------------------------------
# Login / password endpoints (existing)
# ---------------------------------------------------------------------------


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, req: LoginRequest, db: Session = Depends(get_db)):
    user = check_credentials(db, req.login, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    # Track last login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return TokenResponse(access_token=_issue_token(user))


@router.post("/switch-role", response_model=TokenResponse)
def switch_role(
    body: SwitchRoleRequest,
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    if body.active_role not in VALID_PORTAL_ROLES:
        raise HTTPException(status_code=400, detail="Неизвестная роль портала")
    pr = portal_roles_for_user(current_user)
    if body.active_role not in pr:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Эта роль не назначена пользователю",
        )
    return TokenResponse(access_token=_issue_token(current_user, body.active_role))


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    pr = portal_roles_for_user(current_user)
    ar = resolve_active_role(current_user, token)
    return MeResponse(
        id=current_user.id,
        login=current_user.login,
        role=current_user.role,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        telegram_username=current_user.telegram_username,
        avatar_url=current_user.avatar_url,
        portal_roles=pr,
        active_role=ar,
        tenant_id=current_user.tenant_id,
        team_id=current_user.team_id,
        storage_quota_bytes=current_user.storage_quota_bytes or 0,
        storage_used_bytes=current_user.storage_used_bytes or 0,
    )


# ---------------------------------------------------------------------------
# Token refresh & sign-out (linza-admin compatibility)
# ---------------------------------------------------------------------------


@router.post("/token")
def refresh_token(current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """Refresh JWT access token. Returns camelCase for linza-admin compat."""
    ar = resolve_active_role(current_user, token)
    return {"accessToken": _issue_token(current_user, ar)}


@router.post("/sign-out")
def sign_out(current_user: User = Depends(get_current_user)):
    """Sign out (stateless JWT — client discards token)."""
    return {"detail": "Signed out"}


# ---------------------------------------------------------------------------
# OTP-based authentication (linza-admin multi-factor flow)
# ---------------------------------------------------------------------------

OTP_EXPIRE_MINUTES = 10


@router.post("/otp/challenge", response_model=OtpChallengeResponse)
@limiter.limit("5/minute")
def otp_challenge(request: Request, body: OtpChallengeRequest, db: Session = Depends(get_db)):
    """Initiate OTP challenge: generate a code and a state token.

    In production, the OTP code should be sent via email/SMS.
    For now, the code is stored hashed and returned in a development header.
    """
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден")

    if body.channel not in ("email", "sms"):
        raise HTTPException(status_code=400, detail="Канал должен быть 'email' или 'sms'")

    otp_code = f"{secrets.randbelow(10**6):06d}"
    state_token = secrets.token_urlsafe(32)

    challenge = OtpChallenge(
        state_token=state_token,
        user_id=user.id,
        otp_code=hash_password(otp_code),
        channel=body.channel,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES),
    )
    db.add(challenge)
    db.commit()

    # TODO: Send OTP via email/SMS service. For now, log it.
    import logging
    logging.getLogger("linza.auth").info("OTP for %s: %s (dev only)", body.email, otp_code)

    return OtpChallengeResponse(state_token=state_token)


@router.post("/otp/verify", response_model=OtpVerifyResponse)
@limiter.limit("10/minute")
def otp_verify(request: Request, body: OtpVerifyRequest, db: Session = Depends(get_db)):
    """Verify OTP code. Returns state_token for sign-in exchange."""
    challenge = db.query(OtpChallenge).filter(
        OtpChallenge.state_token == body.state_token
    ).first()

    if not challenge:
        raise HTTPException(status_code=400, detail="Неверный state token")

    if challenge.verified:
        raise HTTPException(status_code=400, detail="OTP уже использован")

    if _utcnow() > challenge.expires_at.replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="OTP истёк")

    if not verify_password(body.passcode, challenge.otp_code):
        raise HTTPException(status_code=400, detail="Неверный OTP-код")

    challenge.verified = True
    db.commit()

    user = db.query(User).filter(User.id == challenge.user_id).first()

    return OtpVerifyResponse(
        state_token=challenge.state_token,
        user={
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    )


class CompatSignInBody(BaseModel):
    stateToken: str | None = None
    state_token: str | None = None  # accept both formats


@router.post("/sign-in")
def sign_in(body: CompatSignInBody, db: Session = Depends(get_db)):
    """Exchange a verified state token for a JWT access token.

    Accepts both camelCase (stateToken) and snake_case (state_token) for compatibility.
    Returns camelCase accessToken for linza-admin.
    """
    token_value = body.stateToken or body.state_token
    if not token_value:
        raise HTTPException(status_code=400, detail="stateToken is required")

    challenge = db.query(OtpChallenge).filter(
        OtpChallenge.state_token == token_value,
        OtpChallenge.verified == True,
    ).first()

    if not challenge:
        raise HTTPException(status_code=400, detail="Неверный или непроверенный state token")

    if _utcnow() > challenge.expires_at.replace(tzinfo=None) + timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="State token истёк")

    user = db.query(User).filter(User.id == challenge.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.last_login_at = datetime.now(timezone.utc)
    db.delete(challenge)
    db.commit()

    return {"accessToken": _issue_token(user)}


# ---------------------------------------------------------------------------
# Compatibility endpoints for linza-admin (camelCase responses)
# These endpoints emulate the lm-identity-api format so that
# the linza-admin frontend works without auth flow changes.
# ---------------------------------------------------------------------------


class CompatLoginRequest(BaseModel):
    login: str
    password: str


class CompatLoginResponse(BaseModel):
    user: dict
    stateToken: str


class CompatOtpChallengeRequest(BaseModel):
    stateToken: str
    language: str = "ru"


class CompatOtpVerifyRequest(BaseModel):
    stateToken: str
    passcode: str


class CompatOtpVerifyResponse(BaseModel):
    user: dict
    stateToken: str


class CompatSignInRequest(BaseModel):
    stateToken: str


class CompatTokenResponse(BaseModel):
    accessToken: str


@router.post("", response_model=CompatLoginResponse)
@limiter.limit("5/minute")
def compat_login(request: Request, req: CompatLoginRequest, db: Session = Depends(get_db)):
    """Compat: POST /api/auth — validates credentials, creates OTP challenge, returns stateToken."""
    user = check_credentials(db, req.login, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )

    otp_code = f"{secrets.randbelow(10**6):06d}"
    state_token = secrets.token_urlsafe(32)

    challenge = OtpChallenge(
        state_token=state_token,
        user_id=user.id,
        otp_code=hash_password(otp_code),
        channel="email",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES),
    )
    db.add(challenge)
    db.commit()

    import logging
    logging.getLogger("linza.auth").info("OTP for %s: %s (dev only)", user.email, otp_code)

    return CompatLoginResponse(
        user={"id": str(user.id), "email": user.email, "phoneNumber": user.phone_number},
        stateToken=state_token,
    )


@router.post("/factors/otp/challenge/email")
@limiter.limit("5/minute")
def compat_otp_email(request: Request, body: CompatOtpChallengeRequest, db: Session = Depends(get_db)):
    """Compat: resend OTP via email."""
    challenge = db.query(OtpChallenge).filter(OtpChallenge.state_token == body.stateToken).first()
    if not challenge:
        raise HTTPException(status_code=400, detail="Неверный state token")

    otp_code = f"{secrets.randbelow(10**6):06d}"
    challenge.otp_code = hash_password(otp_code)
    challenge.channel = "email"
    challenge.expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
    challenge.verified = False
    db.commit()

    import logging
    user = db.query(User).filter(User.id == challenge.user_id).first()
    logging.getLogger("linza.auth").info("OTP resend for %s: %s (dev only)", user.email if user else "?", otp_code)
    return {"detail": "OTP sent"}


@router.post("/factors/otp/challenge/sms")
@limiter.limit("5/minute")
def compat_otp_sms(request: Request, body: CompatOtpChallengeRequest, db: Session = Depends(get_db)):
    """Compat: resend OTP via SMS."""
    challenge = db.query(OtpChallenge).filter(OtpChallenge.state_token == body.stateToken).first()
    if not challenge:
        raise HTTPException(status_code=400, detail="Неверный state token")

    otp_code = f"{secrets.randbelow(10**6):06d}"
    challenge.otp_code = hash_password(otp_code)
    challenge.channel = "sms"
    challenge.expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
    challenge.verified = False
    db.commit()

    import logging
    user = db.query(User).filter(User.id == challenge.user_id).first()
    logging.getLogger("linza.auth").info("OTP SMS for %s: %s (dev only)", user.phone_number if user else "?", otp_code)
    return {"detail": "OTP sent"}


@router.post("/factors/otp/verify")
@limiter.limit("10/minute")
def compat_factors_otp_verify(request: Request, body: CompatOtpVerifyRequest, db: Session = Depends(get_db)):
    """Compat: POST /api/auth/factors/otp/verify — verify OTP (camelCase stateToken)."""
    challenge = db.query(OtpChallenge).filter(
        OtpChallenge.state_token == body.stateToken,
    ).first()

    if not challenge:
        raise HTTPException(status_code=401, detail="Неверный state token")
    if challenge.verified:
        raise HTTPException(status_code=401, detail="OTP уже использован")
    if _utcnow() > challenge.expires_at.replace(tzinfo=None):
        raise HTTPException(status_code=401, detail="OTP истёк")
    if not verify_password(body.passcode, challenge.otp_code):
        raise HTTPException(status_code=401, detail="Неверный OTP-код")

    challenge.verified = True
    db.commit()

    user = db.query(User).filter(User.id == challenge.user_id).first()
    return CompatOtpVerifyResponse(
        user={"id": str(user.id), "email": user.email, "phoneNumber": user.phone_number},
        stateToken=challenge.state_token,
    )
