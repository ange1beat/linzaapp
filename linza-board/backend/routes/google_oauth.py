"""OAuth Google → токен Drive для личного импорта (на каждого пользователя)."""

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlencode, urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User, UserGoogleDriveToken, GoogleOAuthState
from backend.org_portal_sources import assert_ingest_sources_allowed
from backend.routes.storage_import import (
    _raise_from_storage_response,
    _storage_base,
    _svc_headers,
)

logger = logging.getLogger("linza-board.google_oauth")

router = APIRouter()

CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "").strip()
FRONTEND_BASE = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
SCOPE = os.getenv(
    "GOOGLE_OAUTH_SCOPE",
    "https://www.googleapis.com/auth/drive.readonly",
).strip()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def _oauth_configured() -> bool:
    return bool(CLIENT_ID and CLIENT_SECRET and REDIRECT_URI)


def _pick_redirect_base(preference: str | None) -> str:
    p = (preference or "").strip().rstrip("/")
    return p or FRONTEND_BASE


def _allowed_frontend_origin(origin: str) -> str:
    o = (origin or "").strip().rstrip("/")
    if not o:
        return ""
    if "://" not in o:
        o = "http://" + o
    return _frontend_base_from_referer(o + "/")


def _frontend_base_from_referer(referer: str) -> str:
    if not (referer or "").strip():
        return ""
    try:
        ref = urlparse(referer.strip())
        redir = urlparse(REDIRECT_URI)
        if ref.scheme not in ("http", "https") or not ref.netloc:
            return ""
        ref_host = (ref.hostname or "").lower()
        allowed = (redir.hostname or "").lower()
        if ref_host in ("localhost", "127.0.0.1"):
            return f"{ref.scheme}://{ref.netloc}".rstrip("/")
        if allowed and ref_host == allowed:
            return f"{ref.scheme}://{ref.netloc}".rstrip("/")
    except Exception:
        return ""
    return ""


def _redirect_err(msg: str, base: str | None = None) -> RedirectResponse:
    b = _pick_redirect_base(base)
    return RedirectResponse(url=f"{b}/files?google_error={quote(msg, safe='')}")


def _redirect_ok(base: str | None = None) -> RedirectResponse:
    b = _pick_redirect_base(base)
    return RedirectResponse(url=f"{b}/files?google_connected=1")


def _parse_expires(data: dict) -> datetime | None:
    raw = data.get("expires_in")
    if raw is None:
        return None
    try:
        sec = int(raw)
    except (TypeError, ValueError):
        return None
    return datetime.now(timezone.utc) + timedelta(seconds=sec)


class GoogleStartBody(BaseModel):
    frontend_origin: str = ""


def _refresh_access_token(db: Session, row: UserGoogleDriveToken) -> None:
    rt = (row.refresh_token or "").strip()
    if not rt:
        raise HTTPException(
            status_code=400,
            detail="Google: нет refresh token — отключите Диск и войдите снова (нужен доступ offline).",
        )
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            GOOGLE_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": rt,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if r.status_code >= 400:
        logger.warning("google token refresh failed: %s %s", r.status_code, r.text[:500])
        raise HTTPException(status_code=400, detail="Google: не удалось обновить сессию — войдите снова.")
    payload = r.json()
    access = payload.get("access_token")
    if not access:
        raise HTTPException(status_code=400, detail="Google: пустой ответ при обновлении токена")
    row.access_token = access
    new_exp = _parse_expires(payload)
    if new_exp:
        row.expires_at = new_exp
    db.add(row)
    db.commit()


def _access_token_fresh(db: Session, row: UserGoogleDriveToken) -> str:
    now = datetime.now(timezone.utc)
    exp = row.expires_at
    if exp is not None:
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp > now + timedelta(seconds=90):
            return row.access_token
    elif not (row.refresh_token or "").strip():
        return row.access_token
    _refresh_access_token(db, row)
    return row.access_token


@router.post("/start")
async def google_oauth_start(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _oauth_configured():
        raise HTTPException(
            status_code=503,
            detail="Google OAuth не настроен: задайте GOOGLE_OAUTH_CLIENT_ID, "
            "GOOGLE_OAUTH_CLIENT_SECRET, GOOGLE_OAUTH_REDIRECT_URI",
        )
    assert_ingest_sources_allowed(db, "google")
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    db.query(GoogleOAuthState).filter(GoogleOAuthState.created_at < cutoff).delete(
        synchronize_session=False
    )
    state = secrets.token_urlsafe(32)
    payload = GoogleStartBody()
    try:
        raw = await request.json()
        if isinstance(raw, dict) and raw.get("frontend_origin"):
            payload = GoogleStartBody(frontend_origin=str(raw.get("frontend_origin") or ""))
    except Exception:
        pass
    fb = _allowed_frontend_origin(payload.frontend_origin)
    if not fb:
        fb = _frontend_base_from_referer(request.headers.get("referer", ""))
    db.add(GoogleOAuthState(state=state, user_id=current_user.id, frontend_base=fb or ""))
    db.commit()
    qs = urlencode(
        {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
        }
    )
    return {"authorize_url": f"{GOOGLE_AUTH_URL}?{qs}"}


@router.get("/callback")
def google_oauth_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: Session = Depends(get_db),
):
    if error:
        msg = error_description or error
        return _redirect_err(msg or "OAuth отменён")
    if not code or not state:
        return _redirect_err("Нет code или state")
    st = db.query(GoogleOAuthState).filter(GoogleOAuthState.state == state).first()
    if not st:
        return _redirect_err("Сессия входа устарела — попробуйте снова")
    back = _pick_redirect_base(getattr(st, "frontend_base", None) or None)
    created = st.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - created > timedelta(minutes=15):
        db.delete(st)
        db.commit()
        return _redirect_err("Истёк срок входа — попробуйте снова", back)
    user_id = st.user_id
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if r.status_code >= 400:
            logger.warning("google token exchange failed: %s %s", r.status_code, r.text[:500])
            db.delete(st)
            db.commit()
            return _redirect_err("Не удалось получить токен Google", back)
        payload = r.json()
        access = payload.get("access_token")
        if not access:
            db.delete(st)
            db.commit()
            return _redirect_err("Пустой ответ Google OAuth", back)
        refresh = (payload.get("refresh_token") or "") or ""
        expires_at = _parse_expires(payload)
        row = db.query(UserGoogleDriveToken).filter(UserGoogleDriveToken.user_id == user_id).first()
        if row:
            row.access_token = access
            if refresh:
                row.refresh_token = refresh
            row.expires_at = expires_at
        else:
            db.add(
                UserGoogleDriveToken(
                    user_id=user_id,
                    access_token=access,
                    refresh_token=refresh,
                    expires_at=expires_at,
                )
            )
        db.delete(st)
        db.commit()
        logger.info("google oauth token saved for user_id=%s", user_id)
        return _redirect_ok(back)
    except Exception as exc:
        logger.exception("google_oauth_callback: %s", exc)
        db.rollback()
        return _redirect_err("Ошибка сервера при подключении Google", back)


@router.get("/status")
def google_connection_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(UserGoogleDriveToken)
        .filter(UserGoogleDriveToken.user_id == current_user.id)
        .first()
    )
    ok = row is not None
    # Иначе nginx/браузер может отдать старый JSON — UI вечно «не подключено».
    return JSONResponse(
        content={"connected": ok},
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
        },
    )


@router.delete("/disconnect")
def google_disconnect(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(UserGoogleDriveToken).filter(UserGoogleDriveToken.user_id == current_user.id).delete(
        synchronize_session=False
    )
    db.commit()
    return {"status": "ok"}


class GoogleMeListBody(BaseModel):
    prefix: str = ""
    root_path: str = ""
    max_keys: int = Field(default=500, ge=1, le=1000)


class GoogleMeImportBody(BaseModel):
    keys: list[str] = Field(min_length=1)


def _require_user_google_token(db: Session, user: User) -> UserGoogleDriveToken:
    row = (
        db.query(UserGoogleDriveToken)
        .filter(UserGoogleDriveToken.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(
            status_code=400,
            detail="Google Диск не подключён. Нажмите «Войти через Google» в окне добавления файлов.",
        )
    return row


@router.post("/files/list")
async def google_me_list(
    body: GoogleMeListBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    assert_ingest_sources_allowed(db, "google")
    row = _require_user_google_token(db, user)
    token = _access_token_fresh(db, row)
    payload = {
        "provider": "google_drive",
        "oauth_token": token,
        "root_path": body.root_path.strip(),
        "prefix": body.prefix.strip(),
        "max_keys": body.max_keys,
        "endpoint_url": "",
        "bucket_name": "",
        "access_key_id": "",
        "secret_access_key": "",
        "region": "us-east-1",
    }
    url = _storage_base() + "/api/files/remote-s3/list"
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=30.0)) as client:
        r = await client.post(url, json=payload, headers=_svc_headers())
    if r.status_code >= 400:
        _raise_from_storage_response(r)
    return r.json()


@router.post("/files/import")
async def google_me_import(
    body: GoogleMeImportBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    assert_ingest_sources_allowed(db, "google")
    row = _require_user_google_token(db, user)
    token = _access_token_fresh(db, row)
    payload = {
        "provider": "google_drive",
        "oauth_token": token,
        "keys": body.keys,
        "endpoint_url": "",
        "bucket_name": "",
        "access_key_id": "",
        "secret_access_key": "",
        "region": "us-east-1",
    }
    url = _storage_base() + "/api/files/remote-s3/import"
    async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
        r = await client.post(url, json=payload, headers=_svc_headers())
    if r.status_code >= 400:
        _raise_from_storage_response(r)
    return r.json()
