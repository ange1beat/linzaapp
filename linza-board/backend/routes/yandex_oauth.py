"""OAuth Яндекс ID → токен Диска для личного импорта (на каждого пользователя)."""

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
from backend.models import User, UserYandexDiskToken, YandexOAuthState
from backend.org_portal_sources import assert_ingest_sources_allowed
from backend.routes.storage_import import (
    _normalize_yandex_root,
    _raise_from_storage_response,
    _storage_base,
    _svc_headers,
)

logger = logging.getLogger("linza-board.yandex_oauth")

router = APIRouter()

CLIENT_ID = os.getenv("YANDEX_OAUTH_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("YANDEX_OAUTH_CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("YANDEX_OAUTH_REDIRECT_URI", "").strip()
FRONTEND_BASE = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
SCOPE = os.getenv("YANDEX_OAUTH_SCOPE", "cloud_api:disk.read")


def _oauth_configured() -> bool:
    return bool(CLIENT_ID and CLIENT_SECRET and REDIRECT_URI)


def _pick_redirect_base(preference: str | None) -> str:
    p = (preference or "").strip().rstrip("/")
    return p or FRONTEND_BASE


def _allowed_frontend_origin(origin: str) -> str:
    """То же правило хоста, что для Referer; origin = window.location.origin с фронта."""
    o = (origin or "").strip().rstrip("/")
    if not o:
        return ""
    if "://" not in o:
        o = "http://" + o
    return _frontend_base_from_referer(o + "/")


def _frontend_base_from_referer(referer: str) -> str:
    """Origin страницы, с которой нажали «Войти» — в Docker это :8000, а не :5173 из .env по умолчанию."""
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
    # Сразу «Источники» — баннер и импорт там; / дал бы аналитику «как будто ничего не случилось»
    return RedirectResponse(url=f"{b}/files?yandex_error={quote(msg, safe='')}")


def _redirect_ok(base: str | None = None) -> RedirectResponse:
    b = _pick_redirect_base(base)
    return RedirectResponse(url=f"{b}/files?yandex_connected=1")


def _parse_expires(data: dict) -> datetime | None:
    raw = data.get("expires_in")
    if raw is None:
        return None
    try:
        sec = int(raw)
    except (TypeError, ValueError):
        return None
    return datetime.now(timezone.utc) + timedelta(seconds=sec)


class YandexStartBody(BaseModel):
    """Явный origin SPA (надёжнее Referer при строгих политиках заголовков)."""

    frontend_origin: str = ""


@router.post("/start")
async def yandex_oauth_start(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Возвращает URL Яндекс OAuth; фронт делает window.location = authorize_url."""
    if not _oauth_configured():
        raise HTTPException(
            status_code=503,
            detail="Яндекс OAuth не настроен: задайте YANDEX_OAUTH_CLIENT_ID, "
            "YANDEX_OAUTH_CLIENT_SECRET, YANDEX_OAUTH_REDIRECT_URI",
        )
    assert_ingest_sources_allowed(db, "yadisk")
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    db.query(YandexOAuthState).filter(YandexOAuthState.created_at < cutoff).delete(
        synchronize_session=False
    )
    state = secrets.token_urlsafe(32)
    payload = YandexStartBody()
    try:
        raw = await request.json()
        if isinstance(raw, dict) and raw.get("frontend_origin"):
            payload = YandexStartBody(frontend_origin=str(raw.get("frontend_origin") or ""))
    except Exception:
        pass
    fb = _allowed_frontend_origin(payload.frontend_origin)
    if not fb:
        fb = _frontend_base_from_referer(request.headers.get("referer", ""))
    db.add(YandexOAuthState(state=state, user_id=current_user.id, frontend_base=fb or ""))
    db.commit()
    qs = urlencode(
        {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPE,
            "state": state,
        }
    )
    return {"authorize_url": f"https://oauth.yandex.ru/authorize?{qs}"}


@router.get("/callback")
def yandex_oauth_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: Session = Depends(get_db),
):
    """Яндекс перенаправляет сюда (без JWT). Проверка state, обмен code → токен."""
    if error:
        msg = error_description or error
        return _redirect_err(msg or "OAuth отменён")
    if not code or not state:
        return _redirect_err("Нет code или state")
    st = db.query(YandexOAuthState).filter(YandexOAuthState.state == state).first()
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
                "https://oauth.yandex.ru/token",
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
            logger.warning("yandex token exchange failed: %s %s", r.status_code, r.text[:500])
            db.delete(st)
            db.commit()
            return _redirect_err("Не удалось получить токен Яндекса", back)
        payload = r.json()
        access = payload.get("access_token")
        if not access:
            db.delete(st)
            db.commit()
            return _redirect_err("Пустой ответ Яндекс OAuth", back)
        refresh = (payload.get("refresh_token") or "") or ""
        expires_at = _parse_expires(payload)
        row = db.query(UserYandexDiskToken).filter(UserYandexDiskToken.user_id == user_id).first()
        if row:
            row.access_token = access
            row.refresh_token = refresh or row.refresh_token
            row.expires_at = expires_at
        else:
            db.add(
                UserYandexDiskToken(
                    user_id=user_id,
                    access_token=access,
                    refresh_token=refresh,
                    expires_at=expires_at,
                )
            )
        db.delete(st)
        db.commit()
        return _redirect_ok(back)
    except Exception as exc:
        logger.exception("yandex_oauth_callback: %s", exc)
        db.rollback()
        return _redirect_err("Ошибка сервера при подключении Яндекса", back)


@router.get("/status")
def yandex_connection_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(UserYandexDiskToken)
        .filter(UserYandexDiskToken.user_id == current_user.id)
        .first()
    )
    ok = row is not None
    return JSONResponse(
        content={"connected": ok},
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
        },
    )


@router.delete("/disconnect")
def yandex_disconnect(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(UserYandexDiskToken).filter(UserYandexDiskToken.user_id == current_user.id).delete(
        synchronize_session=False
    )
    db.commit()
    return {"status": "ok"}


class YandexMeListBody(BaseModel):
    prefix: str = ""
    root_path: str = ""
    max_keys: int = Field(default=500, ge=1, le=1000)


class YandexMeImportBody(BaseModel):
    keys: list[str] = Field(min_length=1)


def _require_user_yandex_token(db: Session, user: User) -> UserYandexDiskToken:
    row = (
        db.query(UserYandexDiskToken)
        .filter(UserYandexDiskToken.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(
            status_code=400,
            detail="Яндекс.Диск не подключён. Нажмите «Войти через Яндекс» в окне добавления файлов.",
        )
    return row


@router.post("/files/list")
async def yandex_me_list(
    body: YandexMeListBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Список видео/аудио с Диска пользователя (доска → storage-service, токен не в браузере)."""
    assert_ingest_sources_allowed(db, "yadisk")
    row = _require_user_yandex_token(db, user)
    payload = {
        "provider": "yandex_disk",
        "oauth_token": row.access_token,
        "root_path": _normalize_yandex_root(body.root_path),
        "prefix": body.prefix.strip(),
        "max_keys": body.max_keys,
        "endpoint_url": "",
        "bucket_name": "",
        "access_key_id": "",
        "secret_access_key": "",
        "region": "ru-1",
    }
    url = _storage_base() + "/api/files/remote-s3/list"
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=30.0)) as client:
        r = await client.post(url, json=payload, headers=_svc_headers())
    if r.status_code >= 400:
        _raise_from_storage_response(r)
    return r.json()


@router.post("/files/import")
async def yandex_me_import(
    body: YandexMeImportBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    assert_ingest_sources_allowed(db, "yadisk")
    row = _require_user_yandex_token(db, user)
    payload = {
        "provider": "yandex_disk",
        "oauth_token": row.access_token,
        "keys": body.keys,
        "endpoint_url": "",
        "bucket_name": "",
        "access_key_id": "",
        "secret_access_key": "",
        "region": "ru-1",
    }
    url = _storage_base() + "/api/files/remote-s3/import"
    async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
        r = await client.post(url, json=payload, headers=_svc_headers())
    if r.status_code >= 400:
        _raise_from_storage_response(r)
    return r.json()
