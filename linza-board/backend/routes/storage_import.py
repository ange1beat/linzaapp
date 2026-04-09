"""Импорт с внешнего S3 по сохранённому профилю источника (секреты не уходят в браузер)."""

import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import StorageProfile, User
from backend.org_portal_sources import assert_ingest_sources_allowed, get_sources_enabled

router = APIRouter(tags=["files-remote-profiles"])


_SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "")


def _svc_headers() -> dict:
    return {"X-Service-Key": _SERVICE_API_KEY} if _SERVICE_API_KEY else {}


def _storage_base() -> str:
    raw = os.getenv("STORAGE_SERVICE_URL", "").strip()
    if raw:
        return raw.rstrip("/")
    if os.path.exists("/.dockerenv"):
        return "http://storage-service:8001"
    return "http://127.0.0.1:8001"


class ListByProfileBody(BaseModel):
    profile_id: int
    prefix: str = ""
    max_keys: int = Field(default=500, ge=1, le=1000)


class ImportByProfileBody(BaseModel):
    profile_id: int
    keys: list[str] = Field(min_length=1)


def _get_source_profile(db: Session, profile_id: int) -> StorageProfile:
    p = (
        db.query(StorageProfile)
        .filter(
            StorageProfile.id == profile_id,
            StorageProfile.profile_type == "source",
        )
        .first()
    )
    if not p:
        raise HTTPException(status_code=404, detail="Профиль источника не найден")
    return p


def _normalize_yandex_root(bucket_name: str) -> str:
    b = (bucket_name or "").strip()
    if not b:
        return ""
    if b.lower().startswith("disk:"):
        return b.rstrip("/")
    if b.startswith("/"):
        return "disk:" + b.rstrip("/")
    return "disk:/" + b.replace("\\", "/").strip("/")


def _is_yandex_profile(p: StorageProfile) -> bool:
    return (p.s3_endpoint_url or "").strip().lower() == "yandex-disk"


def _credentials_payload(p: StorageProfile) -> dict:
    if _is_yandex_profile(p):
        return {
            "provider": "yandex_disk",
            "oauth_token": p.s3_secret_access_key,
            "root_path": _normalize_yandex_root(p.s3_bucket_name),
            "endpoint_url": "",
            "bucket_name": "",
            "access_key_id": "",
            "secret_access_key": "",
            "region": "ru-1",
        }
    reg = (p.s3_region or "").strip() or "ru-1"
    return {
        "provider": "s3",
        "endpoint_url": p.s3_endpoint_url,
        "bucket_name": p.s3_bucket_name.strip(),
        "access_key_id": p.s3_access_key_id,
        "secret_access_key": p.s3_secret_access_key,
        "region": reg,
    }


def _raise_from_storage_response(r: httpx.Response) -> None:
    try:
        data = r.json()
    except Exception:
        raise HTTPException(status_code=502, detail=(r.text or "storage-service")) from None
    detail = data.get("detail", "ошибка storage-service")
    if isinstance(detail, list):
        detail = "; ".join(
            str(item.get("msg", item)) if isinstance(item, dict) else str(item) for item in detail
        )
    raise HTTPException(status_code=r.status_code, detail=str(detail))


@router.get("/remote-s3/source-profiles")
def list_source_profiles_for_import(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Список профилей типа «источник» для выбора в модалке (без секретов)."""
    rows = (
        db.query(StorageProfile)
        .filter(StorageProfile.profile_type == "source")
        .order_by(StorageProfile.name)
        .all()
    )
    enabled = set(get_sources_enabled(db))
    out = []
    for p in rows:
        is_y = _is_yandex_profile(p)
        if is_y and "yadisk" not in enabled:
            continue
        if not is_y and "s3" not in enabled:
            continue
        out.append(
            {
                "id": p.id,
                "name": p.name,
                "bucket": p.s3_bucket_name,
                "endpoint_url": p.s3_endpoint_url,
                "region": (p.s3_region or "").strip() or "ru-1",
                "provider": "yandex_disk" if is_y else "s3",
            }
        )
    return out


@router.post("/remote-s3/list-by-profile")
async def remote_list_by_profile(
    body: ListByProfileBody,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    p = _get_source_profile(db, body.profile_id)
    if _is_yandex_profile(p):
        assert_ingest_sources_allowed(db, "yadisk")
    else:
        assert_ingest_sources_allowed(db, "s3")
    payload = {
        **_credentials_payload(p),
        "prefix": body.prefix.strip(),
        "max_keys": body.max_keys,
    }
    url = _storage_base() + "/api/files/remote-s3/list"
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=30.0)) as client:
        r = await client.post(url, json=payload, headers=_svc_headers())
    if r.status_code >= 400:
        _raise_from_storage_response(r)
    return r.json()


@router.post("/remote-s3/import-by-profile")
async def remote_import_by_profile(
    body: ImportByProfileBody,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    p = _get_source_profile(db, body.profile_id)
    if _is_yandex_profile(p):
        assert_ingest_sources_allowed(db, "yadisk")
    else:
        assert_ingest_sources_allowed(db, "s3")
    payload = {**_credentials_payload(p), "keys": body.keys}
    url = _storage_base() + "/api/files/remote-s3/import"
    async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
        r = await client.post(url, json=payload, headers=_svc_headers())
    if r.status_code >= 400:
        _raise_from_storage_response(r)
    return r.json()


@router.post("/remote-s3/list")
async def remote_s3_list_manual(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Ручной S3: org-config; иначе запрос ушёл бы в прокси storage без проверки."""
    assert_ingest_sources_allowed(db, "s3")
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Некорректное JSON-тело") from None
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Ожидался JSON-объект")
    url = _storage_base() + "/api/files/remote-s3/list"
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=30.0)) as client:
        r = await client.post(url, json=payload, headers=_svc_headers())
    if r.status_code >= 400:
        _raise_from_storage_response(r)
    return r.json()


@router.post("/remote-s3/import")
async def remote_s3_import_manual(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    assert_ingest_sources_allowed(db, "s3")
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Некорректное JSON-тело") from None
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Ожидался JSON-объект")
    url = _storage_base() + "/api/files/remote-s3/import"
    async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
        r = await client.post(url, json=payload, headers=_svc_headers())
    if r.status_code >= 400:
        _raise_from_storage_response(r)
    return r.json()
