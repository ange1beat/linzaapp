"""Публичная одноразовая (по TTL) выдача видео для Линза.Детектор — GET source URL.

Не требует JWT: доступ только по подписанному токену (query ?token=… или legacy путь /{token}).
"""

import httpx
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse

from backend.detector_service import encode_download_path, parse_detector_fetch_token, validate_storage_key_for_fetch

router = APIRouter(tags=["detector-fetch"])


def _svc_headers() -> dict[str, str]:
    import os

    k = os.getenv("SERVICE_API_KEY", "").strip()
    return {"X-Service-Key": k} if k else {}


def _storage_base() -> str:
    import os

    raw = os.getenv("STORAGE_SERVICE_URL", "").strip()
    if raw:
        return raw.rstrip("/")
    if os.path.exists("/.dockerenv"):
        return "http://storage-service:8001"
    return "http://127.0.0.1:8001"


def _validated_key_from_token(token: str) -> str:
    t = (token or "").strip()
    if not t:
        raise HTTPException(status_code=400, detail="Отсутствует token")
    raw_key = parse_detector_fetch_token(t)
    if not raw_key:
        raise HTTPException(status_code=404, detail="Недействительная или просроченная ссылка")
    try:
        return validate_storage_key_for_fetch(raw_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def _download_url_for_key(key: str) -> str:
    enc = encode_download_path(key)
    return f"{_storage_base()}/api/files/download/{enc}"


@router.head("/detector-fetch")
def detector_fetch_head_query(request: Request, token: str = Query(..., description="Подписанный токен fetch")):
    """HEAD — детектор может запросить размер; токен в query (совместимость с yt-dlp и др.)."""
    key = _validated_key_from_token(token)
    url = _download_url_for_key(key)
    range_h = request.headers.get("range")
    headers = dict(_svc_headers())
    if range_h:
        headers["Range"] = range_h
    try:
        r = httpx.head(url, headers=headers, timeout=120.0, follow_redirects=True)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"storage недоступен: {e}") from e
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text[:500] if r.text else "storage error")
    out = Response(status_code=r.status_code)
    for h in ("content-length", "content-type", "accept-ranges", "content-range"):
        v = r.headers.get(h)
        if v:
            out.headers[h] = v
    return out


@router.get("/detector-fetch")
async def detector_fetch_get_query(request: Request, token: str = Query(..., description="Подписанный токен fetch")):
    key = _validated_key_from_token(token)
    url = _download_url_for_key(key)
    range_h = request.headers.get("range")
    headers = dict(_svc_headers())
    if range_h:
        headers["Range"] = range_h
    timeout = httpx.Timeout(600.0, connect=30.0)
    client = httpx.AsyncClient(timeout=timeout)
    try:
        req = client.build_request("GET", url, headers=headers)
        upstream = await client.send(req, stream=True)
    except httpx.RequestError as e:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"storage недоступен: {e}") from e

    if upstream.status_code >= 400:
        await upstream.aread()
        await upstream.aclose()
        await client.aclose()
        raise HTTPException(status_code=upstream.status_code, detail="Ошибка чтения файла из хранилища")

    drop = {"connection", "transfer-encoding", "content-encoding"}
    out_hdr = {k: v for k, v in upstream.headers.items() if k.lower() not in drop}

    async def stream():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(stream(), status_code=upstream.status_code, headers=dict(out_hdr))


@router.head("/detector-fetch/{token:path}")
def detector_fetch_head(token: str, request: Request):
    """Legacy: токен в пути (старые ссылки)."""
    key = _validated_key_from_token(token)
    url = _download_url_for_key(key)
    range_h = request.headers.get("range")
    headers = dict(_svc_headers())
    if range_h:
        headers["Range"] = range_h
    try:
        r = httpx.head(url, headers=headers, timeout=120.0, follow_redirects=True)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"storage недоступен: {e}") from e
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text[:500] if r.text else "storage error")
    out = Response(status_code=r.status_code)
    for h in ("content-length", "content-type", "accept-ranges", "content-range"):
        v = r.headers.get(h)
        if v:
            out.headers[h] = v
    return out


@router.get("/detector-fetch/{token:path}")
async def detector_fetch_get(token: str, request: Request):
    """Legacy: токен в пути."""
    key = _validated_key_from_token(token)
    url = _download_url_for_key(key)
    range_h = request.headers.get("range")
    headers = dict(_svc_headers())
    if range_h:
        headers["Range"] = range_h
    timeout = httpx.Timeout(600.0, connect=30.0)
    client = httpx.AsyncClient(timeout=timeout)
    try:
        req = client.build_request("GET", url, headers=headers)
        upstream = await client.send(req, stream=True)
    except httpx.RequestError as e:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"storage недоступен: {e}") from e

    if upstream.status_code >= 400:
        await upstream.aread()
        await upstream.aclose()
        await client.aclose()
        raise HTTPException(status_code=upstream.status_code, detail="Ошибка чтения файла из хранилища")

    drop = {"connection", "transfer-encoding", "content-encoding"}
    out_hdr = {k: v for k, v in upstream.headers.items() if k.lower() not in drop}

    async def stream():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(stream(), status_code=upstream.status_code, headers=dict(out_hdr))
