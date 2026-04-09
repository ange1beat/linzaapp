"""URL и заголовки для запросов linza-vpleer → storage-service."""

from urllib.parse import quote

from app.config import SERVICE_API_KEY, STORAGE_SERVICE_URL


def storage_request_headers() -> dict[str, str]:
    k = (SERVICE_API_KEY or "").strip()
    return {"X-Service-Key": k} if k else {}


def build_storage_download_url(filename: str) -> str:
    """Путь download/… с пер-компонентным quote (как в board) для ключей sources/…"""
    raw = (filename or "").replace("\\", "/").strip()
    if raw.startswith("/"):
        raw = raw.lstrip("/")
    parts = [p for p in raw.split("/") if p]
    enc = "/".join(quote(p, safe="") for p in parts)
    return f"{STORAGE_SERVICE_URL.rstrip('/')}/api/files/download/{enc}"
