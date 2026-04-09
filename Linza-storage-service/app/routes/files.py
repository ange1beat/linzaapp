import asyncio
import json
import logging
import os
import re
import shutil
import tempfile
import uuid
from urllib.parse import urlparse, unquote, quote as url_quote

TEMP_DIR = os.path.join(tempfile.gettempdir(), "linza-storage")

import boto3
import httpx
from botocore.config import Config
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field, field_validator

from app.s3_client import get_s3, get_bucket
from app.tasks import set_task, update_task, get_task, get_active_tasks

logger = logging.getLogger("storage-service")

router = APIRouter()

CHUNK_SIZE = 512 * 1024  # 512 KB
MAX_LIST_KEYS = 1000
MAX_IMPORT_KEYS = 100

# User uploads / our S3 vs content pulled from external sources (for split lists in UI)
UPLOAD_PREFIX = "uploads/"
SOURCE_PREFIX = "sources/"


def validate_s3_key(key: str) -> str:
    """Validate user-supplied S3 key against path traversal and prefix rules.

    Raises HTTPException(400) if key is unsafe.
    Returns the cleaned key.
    """
    key = (key or "").strip().replace("\\", "/")
    if not key:
        raise HTTPException(400, "Key must not be empty")
    if key.startswith("/"):
        raise HTTPException(400, "Absolute paths not allowed")
    if ".." in key.split("/"):
        raise HTTPException(400, "Path traversal not allowed")
    if not (key.startswith(UPLOAD_PREFIX) or key.startswith(SOURCE_PREFIX)):
        raise HTTPException(400, "Access restricted to uploads/ and sources/ prefixes")
    return key


def _safe_basename(name: str) -> str:
    base = os.path.basename((name or "").replace("\\", "/"))
    if not base or base in (".", ".."):
        return f"file_{uuid.uuid4().hex[:8]}.bin"
    return base


def upload_storage_key(original_name: str) -> str:
    """S3 key for files added via this app (local, URL) — stored under uploads/."""
    return UPLOAD_PREFIX + _safe_basename(original_name)


def source_import_storage_key(remote_key: str) -> str:
    """S3 key for objects copied from an external S3 — stored under sources/."""
    rk = (remote_key or "").lstrip("/").replace("\\", "/")
    if rk.lower().startswith("disk:"):
        rk = rk[5:].lstrip("/")
    while rk.startswith(UPLOAD_PREFIX) or rk.startswith(SOURCE_PREFIX):
        parts = rk.split("/", 1)
        rk = parts[1] if len(parts) > 1 else ""
    if not rk:
        rk = f"object_{uuid.uuid4().hex[:8]}"
    return SOURCE_PREFIX + rk


def _partition_file_groups(files: list[dict]) -> tuple[list[dict], list[dict]]:
    uploads: list[dict] = []
    from_sources: list[dict] = []
    for f in files:
        n = (f.get("name") or "").strip()
        if not n:
            continue
        if n.startswith(SOURCE_PREFIX):
            from_sources.append(f)
        else:
            uploads.append(f)
    return uploads, from_sources


def _safe_content_disposition(name: str, disposition: str = "inline") -> str:
    """Build Content-Disposition header safe from header injection (RFC 5987)."""
    encoded = url_quote(name, safe="")
    return f"{disposition}; filename*=UTF-8''{encoded}"


# ── helpers ────────────────────────────────────────────────────────────────────

def _extract_filename(url: str, content_disposition: str | None) -> str:
    if content_disposition:
        m = re.search(r'filename\*?=["\']?(?:UTF-8\'\')?([^"\'\n;]+)', content_disposition, re.IGNORECASE)
        if m:
            return unquote(m.group(1).strip())
    path = urlparse(url).path
    name = unquote(path.split("/")[-1].split("?")[0])
    return name or f"file_{uuid.uuid4().hex[:8]}"


def _remote_s3_client(
    endpoint_url: str,
    access_key_id: str,
    secret_access_key: str,
    region: str,
):
    ep = endpoint_url.strip().rstrip("/")
    if not ep:
        raise ValueError("endpoint_url is required")
    return boto3.client(
        "s3",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        endpoint_url=ep,
        region_name=(region or "us-east-1").strip() or "us-east-1",
        config=Config(signature_version="s3v4"),
    )


def _s3_obj_to_file_row(obj: dict) -> dict | None:
    key = obj.get("Key")
    if not key:
        return None
    try:
        size = int(obj.get("Size", 0) or 0)
    except (TypeError, ValueError):
        size = 0
    lm = obj.get("LastModified")
    if lm is not None and hasattr(lm, "isoformat"):
        last_modified = lm.isoformat()
    else:
        last_modified = ""
    return {"name": key, "size": size, "last_modified": last_modified}


def _list_s3_files() -> list[dict]:
    try:
        resp = get_s3().list_objects_v2(Bucket=get_bucket())
        contents = resp.get("Contents") or []
        rows = [_s3_obj_to_file_row(obj) for obj in contents]
        return [r for r in rows if r is not None]
    except Exception as exc:
        logger.error("S3 list_objects failed for bucket=%s: %s", get_bucket(), exc, exc_info=True)
        return []


# ── background upload task ─────────────────────────────────────────────────────

def _upload_task(task_id: str, url: str, dest_key: str):
    tmp_path = None
    try:
        # ── Phase 1: download to temp file ──────────────────────────────────
        set_task(task_id, {
            "status": "downloading",
            "filename": dest_key,
            "progress": 0,
            "total": 0,
        })

        with httpx.Client(follow_redirects=True, timeout=None) as client:
            with client.stream("GET", url) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("content-length", 0))
                update_task(task_id, total=total)

                suffix = os.path.splitext(dest_key)[1] or ".tmp"
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="storage-", dir=TEMP_DIR)
                downloaded = 0
                with os.fdopen(tmp_fd, "wb") as f:
                    for chunk in resp.iter_bytes(CHUNK_SIZE):
                        f.write(chunk)
                        downloaded += len(chunk)
                        update_task(task_id, progress=downloaded)

        # ── Phase 2: upload to S3 ────────────────────────────────────────────
        file_size = os.path.getsize(tmp_path)
        uploaded = [0]

        def _s3_progress(n: int):
            uploaded[0] += n
            update_task(task_id, status="uploading", progress=uploaded[0], total=file_size)

        update_task(task_id, status="uploading", progress=0, total=file_size)
        get_s3().upload_file(tmp_path, get_bucket(), dest_key, Callback=_s3_progress)

        update_task(task_id, status="completed", progress=file_size, total=file_size)
        logger.info(
            "S3 upload OK: key=%s bucket=%s size_bytes=%s task_id=%s",
            dest_key,
            get_bucket(),
            file_size,
            task_id,
        )

    except Exception as exc:
        logger.error(
            "S3 upload failed: key=%s bucket=%s task_id=%s: %s",
            dest_key,
            get_bucket(),
            task_id,
            exc,
            exc_info=True,
        )
        update_task(task_id, status="error", error=str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _upload_from_path_task(task_id: str, tmp_path: str, dest_key: str):
    """Upload a file already on disk to the configured bucket (then delete temp)."""
    try:
        file_size = os.path.getsize(tmp_path)
        uploaded = [0]

        def _cb(n: int):
            uploaded[0] += n
            update_task(task_id, status="uploading", progress=uploaded[0], total=file_size)

        update_task(task_id, status="uploading", progress=0, total=file_size)
        get_s3().upload_file(tmp_path, get_bucket(), dest_key, Callback=_cb)

        update_task(task_id, status="completed", progress=file_size, total=file_size)
        logger.info(
            "S3 upload OK (local file): key=%s bucket=%s size_bytes=%s task_id=%s",
            dest_key,
            get_bucket(),
            file_size,
            task_id,
        )
    except Exception as exc:
        logger.error(
            "S3 upload from local failed: key=%s task_id=%s: %s",
            dest_key,
            task_id,
            exc,
            exc_info=True,
        )
        update_task(task_id, status="error", error=str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _import_remote_s3_task(
    task_id: str,
    endpoint_url: str,
    bucket_name: str,
    access_key_id: str,
    secret_access_key: str,
    region: str,
    keys: list[str],
):
    remote = _remote_s3_client(endpoint_url, access_key_id, secret_access_key, region)
    n_files = len(keys)
    tmp_path = None
    try:
        for i, key in enumerate(keys):
            dest_key_preview = source_import_storage_key(key)
            set_task(task_id, {
                "status": "downloading_from_remote",
                "filename": dest_key_preview,
                "progress": 0,
                "total": 0,
                "batch_index": i + 1,
                "batch_total": n_files,
            })
            suffix = os.path.splitext(key)[1] or ".bin"
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="storage-", dir=TEMP_DIR)
            os.close(tmp_fd)
            remote.download_file(bucket_name, key, tmp_path)
            file_size = os.path.getsize(tmp_path)
            dest_key = source_import_storage_key(key)

            uploaded = [0]

            def _cb(n: int, uploaded=uploaded):
                uploaded[0] += n
                update_task(
                    task_id,
                    status="uploading",
                    filename=dest_key,
                    progress=uploaded[0],
                    total=file_size,
                    batch_index=i + 1,
                    batch_total=n_files,
                )

            update_task(
                task_id,
                status="uploading",
                progress=0,
                total=file_size,
                filename=dest_key,
                batch_index=i + 1,
                batch_total=n_files,
            )
            get_s3().upload_file(tmp_path, get_bucket(), dest_key, Callback=_cb)
            os.unlink(tmp_path)
            tmp_path = None

            logger.info(
                "Remote S3 import OK: src_bucket=%s src_key=%s dest_key=%s dest_bucket=%s task_id=%s",
                bucket_name,
                key,
                dest_key,
                get_bucket(),
                task_id,
            )

        last = get_task(task_id)
        last_total = last.get("total", 0)
        final_key = source_import_storage_key(keys[-1])
        update_task(
            task_id,
            status="completed",
            filename=final_key,
            progress=last_total,
            total=last_total,
            batch_index=n_files,
            batch_total=n_files,
        )
        logger.info("Remote S3 batch import completed: files=%s task_id=%s", n_files, task_id)
    except Exception as exc:
        logger.error(
            "Remote S3 import failed task_id=%s: %s",
            task_id,
            exc,
            exc_info=True,
        )
        update_task(task_id, status="error", error=str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


YANDEX_DISK_API = "https://cloud-api.yandex.net/v1/disk"

_YANDEX_MEDIA_FILE_RE = re.compile(
    r"\.(mp4|avi|mkv|mov|webm|m4v|wmv|mpeg|mpg|mpe|3gp|ts|mts|m2ts|mp3|wav|aac|m4a|flac|ogg|opus|wma|aiff?|oga)$",
    re.I,
)


def _yandex_oauth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"OAuth {token.strip()}"}


def _yandex_api_path_to_disk_uri(path: str) -> str:
    """API в примерах отдаёт disk:/..., но встречается и /disk/... — для фильтра и download нужен единый вид."""
    p = (path or "").strip()
    if not p:
        return ""
    if p.startswith("trash:") or p.startswith("app:"):
        return p
    if p.startswith("disk:"):
        return p
    if p.startswith("/disk/"):
        return "disk:" + p[len("/disk") :]
    if p in ("/disk", "/disk/"):
        return "disk:/"
    return p


def _yandex_is_video_or_audio_item(it: dict) -> bool:
    mt = (it.get("mime_type") or "").lower()
    if mt.startswith("video/") or mt.startswith("audio/"):
        return True
    name = it.get("name") or ""
    return bool(_YANDEX_MEDIA_FILE_RE.search(name))


def _yandex_composite_path(root_path: str, prefix: str) -> str:
    """Build path prefix for filtering flat file list (disk:/folder[/subprefix])."""
    root = (root_path or "").strip().rstrip("/")
    pre = (prefix or "").strip().strip("/")
    if root.lower().startswith("disk:"):
        base = root
    elif root:
        base = "disk:/" + root.lstrip("/")
    else:
        base = ""
    if pre and base:
        return base + "/" + pre
    if pre:
        return "disk:/" + pre
    return base


def _yandex_path_matches(composite: str, disk_uri: str) -> bool:
    """composite в виде disk:/папка; disk_uri после нормализации из ответа API."""
    p = disk_uri or ""
    if p.startswith("trash:"):
        return False
    if not composite:
        return p.startswith("disk:/")
    c = composite.rstrip("/")
    return p == c or p.startswith(c + "/")


def _yandex_disk_list_objects(oauth_token: str, root_path: str, prefix: str, max_keys: int) -> tuple[list[dict], bool]:
    """Flat /resources/files API + path filter (видео и аудио)."""
    headers = _yandex_oauth_headers(oauth_token)
    composite = _yandex_composite_path(root_path, prefix)
    objects: list[dict] = []
    offset = 0
    page_size = min(200, max_keys + 50)
    scanned_pages = 0
    max_pages = 80
    last_page_full = False

    with httpx.Client(timeout=httpx.Timeout(120.0)) as client:
        while len(objects) < max_keys and scanned_pages < max_pages:
            r = client.get(
                f"{YANDEX_DISK_API}/resources/files",
                params={
                    "limit": page_size,
                    "offset": offset,
                    # unknown: часть роликов на Диске без классификации; отсекаем по mime/расширению ниже
                    "media_type": "video,audio,unknown",
                },
                headers=headers,
            )
            if r.status_code == 401:
                raise ValueError("Яндекс.Диск: неверный или просроченный OAuth-токен")
            r.raise_for_status()
            data = r.json()
            items = data.get("items") or []
            if not items:
                break
            last_page_full = len(items) >= page_size
            for it in items:
                if it.get("type") != "file":
                    continue
                if not _yandex_is_video_or_audio_item(it):
                    continue
                raw = it.get("path") or ""
                if (raw or "").startswith("trash:"):
                    continue
                pth = _yandex_api_path_to_disk_uri(raw)
                if not pth:
                    continue
                if not _yandex_path_matches(composite, pth):
                    continue
                lm = it.get("modified") or it.get("created") or ""
                objects.append({
                    "key": pth,
                    "size": int(it.get("size") or 0),
                    "last_modified": lm if isinstance(lm, str) else "",
                })
                if len(objects) >= max_keys:
                    break
            offset += len(items)
            scanned_pages += 1
            if not last_page_full:
                break

    is_truncated = len(objects) >= max_keys or (scanned_pages >= max_pages and last_page_full)
    return objects, is_truncated


def _import_yandex_disk_task(task_id: str, oauth_token: str, keys: list[str]):
    token = oauth_token.strip()
    headers = _yandex_oauth_headers(token)
    n_files = len(keys)
    tmp_path = None
    try:
        with httpx.Client(follow_redirects=True, timeout=None) as client:
            for i, disk_path in enumerate(keys):
                dest_key_preview = source_import_storage_key(disk_path)
                set_task(task_id, {
                    "status": "downloading_from_remote",
                    "filename": dest_key_preview,
                    "progress": 0,
                    "total": 0,
                    "batch_index": i + 1,
                    "batch_total": n_files,
                })
                dr = client.get(
                    f"{YANDEX_DISK_API}/resources/download",
                    params={"path": disk_path},
                    headers=headers,
                )
                if dr.status_code == 401:
                    raise ValueError("Яндекс.Диск: неверный или просроченный OAuth-токен")
                dr.raise_for_status()
                href = (dr.json() or {}).get("href")
                if not href:
                    raise ValueError("Яндекс.Диск: нет ссылки на скачивание")

                suffix = os.path.splitext(disk_path)[1] or ".bin"
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
                os.close(tmp_fd)
                downloaded = 0
                with client.stream("GET", href) as resp:
                    resp.raise_for_status()
                    total = int(resp.headers.get("content-length", 0) or 0)
                    with open(tmp_path, "wb") as f:
                        for chunk in resp.iter_bytes(CHUNK_SIZE):
                            f.write(chunk)
                            downloaded += len(chunk)
                            update_task(
                                task_id,
                                progress=downloaded,
                                total=total or downloaded,
                                filename=dest_key_preview,
                                batch_index=i + 1,
                                batch_total=n_files,
                            )

                file_size = os.path.getsize(tmp_path)
                dest_key = source_import_storage_key(disk_path)
                uploaded = [0]

                def _cb(n: int, uploaded=uploaded):
                    uploaded[0] += n
                    update_task(
                        task_id,
                        status="uploading",
                        filename=dest_key,
                        progress=uploaded[0],
                        total=file_size,
                        batch_index=i + 1,
                        batch_total=n_files,
                    )

                update_task(
                    task_id,
                    status="uploading",
                    progress=0,
                    total=file_size,
                    filename=dest_key,
                    batch_index=i + 1,
                    batch_total=n_files,
                )
                get_s3().upload_file(tmp_path, get_bucket(), dest_key, Callback=_cb)
                os.unlink(tmp_path)
                tmp_path = None

                logger.info(
                    "Yandex Disk import OK: src=%s dest_key=%s dest_bucket=%s task_id=%s",
                    disk_path,
                    dest_key,
                    get_bucket(),
                    task_id,
                )

        last = get_task(task_id)
        last_total = last.get("total", 0)
        final_key = source_import_storage_key(keys[-1])
        update_task(
            task_id,
            status="completed",
            filename=final_key,
            progress=last_total,
            total=last_total,
            batch_index=n_files,
            batch_total=n_files,
        )
        logger.info("Yandex Disk batch import completed: files=%s task_id=%s", n_files, task_id)
    except Exception as exc:
        logger.error("Yandex Disk import failed task_id=%s: %s", task_id, exc, exc_info=True)
        update_task(task_id, status="error", error=str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


GOOGLE_DRIVE_FILES_API = "https://www.googleapis.com/drive/v3/files"

_GOOGLE_MEDIA_FILE_RE = re.compile(
    r"\.(mp4|avi|mkv|mov|webm|m4v|wmv|mpeg|mpg|mpe|3gp|ts|mts|m2ts|mp3|wav|aac|m4a|flac|ogg|opus|wma|aiff?|oga)$",
    re.I,
)


def _google_bearer_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token.strip()}"}


def _google_escape_q_value(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace("'", "\\'")


def _google_is_video_or_audio(mime: str, name: str) -> bool:
    mt = (mime or "").lower()
    if mt.startswith("video/") or mt.startswith("audio/"):
        return True
    if mt == "application/octet-stream":
        return bool(_GOOGLE_MEDIA_FILE_RE.search(name or ""))
    return bool(_GOOGLE_MEDIA_FILE_RE.search(name or ""))


def _google_drive_list_objects(oauth_token: str, root_path: str, prefix: str, max_keys: int) -> tuple[list[dict], bool]:
    """Drive API v3: видео/аудио; root_path = ID папки (необязательно); prefix = подстрока в имени файла."""
    headers = _google_bearer_headers(oauth_token)
    q_parts = [
        "trashed = false",
        "("
        "mimeType contains 'video/' or mimeType contains 'audio/' or "
        "mimeType = 'application/octet-stream'"
        ")",
    ]
    folder_id = (root_path or "").strip()
    if folder_id:
        q_parts.append(f"'{_google_escape_q_value(folder_id)}' in parents")
    name_hint = (prefix or "").strip()
    if name_hint:
        q_parts.append(f"name contains '{_google_escape_q_value(name_hint)}'")
    q = " and ".join(q_parts)

    objects: list[dict] = []
    page_token: str | None = None
    is_truncated = False

    with httpx.Client(timeout=httpx.Timeout(120.0)) as client:
        while len(objects) < max_keys:
            page_size = min(100, max_keys - len(objects))
            if page_size <= 0:
                break
            params: dict = {
                "q": q,
                "spaces": "drive",
                "corpora": "allDrives",
                "fields": "nextPageToken, files(id, name, size, modifiedTime, mimeType)",
                "pageSize": page_size,
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            }
            if page_token:
                params["pageToken"] = page_token
            r = client.get(GOOGLE_DRIVE_FILES_API, params=params, headers=headers)
            if r.status_code == 401:
                raise ValueError("Google Диск: неверный или просроченный OAuth-токен")
            r.raise_for_status()
            data = r.json()
            files = data.get("files") or []
            next_pt = data.get("nextPageToken")
            for f in files:
                fid = f.get("id")
                name = f.get("name") or ""
                mime = f.get("mimeType") or ""
                if not fid:
                    continue
                if not _google_is_video_or_audio(mime, name):
                    continue
                try:
                    size = int(f.get("size") or 0)
                except (TypeError, ValueError):
                    size = 0
                lm = f.get("modifiedTime") or ""
                objects.append({
                    "key": fid,
                    "name": name,
                    "size": size,
                    "last_modified": lm if isinstance(lm, str) else "",
                })
                if len(objects) >= max_keys:
                    is_truncated = bool(next_pt) or len(files) >= page_size
                    break
            if len(objects) >= max_keys:
                is_truncated = is_truncated or bool(next_pt)
                break
            if not next_pt:
                break
            page_token = next_pt

    return objects, is_truncated


def _import_google_drive_task(task_id: str, oauth_token: str, file_ids: list[str]):
    token = oauth_token.strip()
    headers = _google_bearer_headers(token)
    n_files = len(file_ids)
    tmp_path = None
    api_base = GOOGLE_DRIVE_FILES_API
    last_imported_dest_key = ""
    try:
        with httpx.Client(follow_redirects=True, timeout=None) as client:
            for i, fid in enumerate(file_ids):
                fid = (fid or "").strip()
                if not fid:
                    continue
                mr = client.get(
                    f"{api_base}/{fid}",
                    params={"fields": "name,mimeType,size", "supportsAllDrives": "true"},
                    headers=headers,
                )
                if mr.status_code == 401:
                    raise ValueError("Google Диск: неверный или просроченный OAuth-токен")
                mr.raise_for_status()
                meta = mr.json() or {}
                fname = meta.get("name") or f"file_{fid[:12]}"
                mime = (meta.get("mimeType") or "").lower()
                if mime.startswith("application/vnd.google-apps."):
                    raise ValueError(
                        f"Google Диск: «{fname}» — документ Google, а не файл. Выберите обычное видео/аудио."
                    )

                dest_key_preview = source_import_storage_key(fname)
                set_task(task_id, {
                    "status": "downloading_from_remote",
                    "filename": dest_key_preview,
                    "progress": 0,
                    "total": 0,
                    "batch_index": i + 1,
                    "batch_total": n_files,
                })

                suffix = os.path.splitext(fname)[1] or ".bin"
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
                os.close(tmp_fd)
                downloaded = 0
                with client.stream(
                    "GET",
                    f"{api_base}/{fid}",
                    params={"alt": "media", "supportsAllDrives": "true"},
                    headers=headers,
                ) as resp:
                    if resp.status_code == 401:
                        raise ValueError("Google Диск: неверный или просроченный OAuth-токен")
                    resp.raise_for_status()
                    total = int(resp.headers.get("content-length", 0) or 0)
                    with open(tmp_path, "wb") as out:
                        for chunk in resp.iter_bytes(CHUNK_SIZE):
                            out.write(chunk)
                            downloaded += len(chunk)
                            update_task(
                                task_id,
                                progress=downloaded,
                                total=total or downloaded,
                                filename=dest_key_preview,
                                batch_index=i + 1,
                                batch_total=n_files,
                            )

                file_size = os.path.getsize(tmp_path)
                dest_key = source_import_storage_key(fname)
                uploaded = [0]

                def _cb(n: int, uploaded=uploaded):
                    uploaded[0] += n
                    update_task(
                        task_id,
                        status="uploading",
                        filename=dest_key,
                        progress=uploaded[0],
                        total=file_size,
                        batch_index=i + 1,
                        batch_total=n_files,
                    )

                update_task(
                    task_id,
                    status="uploading",
                    progress=0,
                    total=file_size,
                    filename=dest_key,
                    batch_index=i + 1,
                    batch_total=n_files,
                )
                get_s3().upload_file(tmp_path, get_bucket(), dest_key, Callback=_cb)
                os.unlink(tmp_path)
                tmp_path = None
                last_imported_dest_key = dest_key

                logger.info(
                    "Google Drive import OK: src_id=%s dest_key=%s dest_bucket=%s task_id=%s",
                    fid,
                    dest_key,
                    get_bucket(),
                    task_id,
                )

        last = get_task(task_id)
        last_total = last.get("total", 0)
        final_key = last_imported_dest_key or last.get("filename") or ""
        update_task(
            task_id,
            status="completed",
            filename=final_key,
            progress=last_total,
            total=last_total,
            batch_index=n_files,
            batch_total=n_files,
        )
        logger.info("Google Drive batch import completed: files=%s task_id=%s", n_files, task_id)
    except Exception as exc:
        logger.error("Google Drive import failed task_id=%s: %s", task_id, exc, exc_info=True)
        update_task(task_id, status="error", error=str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

def _json_safe_tasks(tasks: list[dict]) -> list[dict]:
    out = []
    for t in tasks:
        row = {}
        for k, v in t.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                row[k] = v
            else:
                row[k] = str(v)
        out.append(row)
    return out


@router.get("", include_in_schema=False)
@router.get("/")
def list_files():
    try:
        all_files = _list_s3_files()
        uploads, from_sources = _partition_file_groups(all_files)
        tasks = _json_safe_tasks(get_active_tasks())
        return {
            "files": all_files,
            "uploads": uploads,
            "from_sources": from_sources,
            "tasks": tasks,
        }
    except Exception as exc:
        logger.exception("list_files failed: %s", exc)
        raise HTTPException(500, detail=f"list_files: {exc}") from exc


class RemoteS3Credentials(BaseModel):
    """S3 credentials (optional when provider is OAuth cloud: yandex_disk, google_drive)."""
    endpoint_url: str = ""
    bucket_name: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
    region: str = Field(default="ru-1")


class RemoteS3ListRequest(RemoteS3Credentials):
    provider: str = Field(default="s3")
    prefix: str = ""
    max_keys: int = Field(default=500, ge=1, le=MAX_LIST_KEYS)
    oauth_token: str = ""
    root_path: str = ""


class RemoteS3ImportRequest(RemoteS3Credentials):
    provider: str = Field(default="s3")
    oauth_token: str = ""
    keys: list[str] = Field(min_length=1)

    @field_validator("keys")
    @classmethod
    def cap_keys(cls, v: list[str]) -> list[str]:
        if len(v) > MAX_IMPORT_KEYS:
            raise ValueError(f"at most {MAX_IMPORT_KEYS} keys per request")
        cleaned = [k.strip() for k in v if k and k.strip()]
        if not cleaned:
            raise ValueError("keys must be non-empty")
        return cleaned


class UploadRequest(BaseModel):
    url: str


@router.post("/upload-from-url")
def upload_from_url(body: UploadRequest, background_tasks: BackgroundTasks):
    url = body.url.strip()
    if not url:
        raise HTTPException(400, "url is required")

    path = urlparse(url).path
    basename = unquote(path.split("/")[-1].split("?")[0]) or f"file_{uuid.uuid4().hex[:8]}"
    dest_key = upload_storage_key(basename)

    task_id = uuid.uuid4().hex
    set_task(task_id, {
        "status": "pending",
        "filename": dest_key,
        "progress": 0,
        "total": 0,
    })
    background_tasks.add_task(_upload_task, task_id, url, dest_key)
    return {"task_id": task_id, "filename": dest_key}


@router.post("/upload-local")
async def upload_local(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    raw_name = file.filename or f"upload_{uuid.uuid4().hex[:8]}.bin"
    dest_key = upload_storage_key(raw_name)
    suffix = os.path.splitext(dest_key)[1] or ".bin"
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="storage-", dir=TEMP_DIR)
    os.close(tmp_fd)
    try:
        with open(tmp_path, "wb") as out:
            shutil.copyfileobj(file.file, out, length=CHUNK_SIZE)
    except Exception as exc:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        logger.error("upload-local save failed: %s", exc, exc_info=True)
        raise HTTPException(400, "Не удалось сохранить файл") from exc

    task_id = uuid.uuid4().hex
    set_task(task_id, {
        "status": "pending",
        "filename": dest_key,
        "progress": 0,
        "total": 0,
    })
    background_tasks.add_task(_upload_from_path_task, task_id, tmp_path, dest_key)
    return {"task_id": task_id, "filename": dest_key}


@router.post("/remote-s3/list")
def remote_s3_list(body: RemoteS3ListRequest):
    prov = (body.provider or "s3").strip().lower()
    oauth = (body.oauth_token or "").strip()
    # Старый board / клиент без поля provider: токен Диска + пустой S3 → это Яндекс, не внешний S3.
    if (
        prov in ("s3", "")
        and oauth
        and not (body.endpoint_url or "").strip()
        and not (body.bucket_name or "").strip()
    ):
        prov = "yandex_disk"
    try:
        if prov in ("yandex_disk", "yandex-disk", "yandex"):
            if not (body.oauth_token or "").strip():
                raise ValueError("Укажите OAuth-токен Яндекс.Диска")
            objects, is_truncated = _yandex_disk_list_objects(
                body.oauth_token,
                body.root_path,
                body.prefix,
                body.max_keys,
            )
            return {"objects": objects, "is_truncated": is_truncated}
        if prov in ("google_drive", "google-drive", "gdrive"):
            if not (body.oauth_token or "").strip():
                raise ValueError("Укажите OAuth-токен Google Диска")
            objects, is_truncated = _google_drive_list_objects(
                body.oauth_token,
                body.root_path,
                body.prefix,
                body.max_keys,
            )
            return {"objects": objects, "is_truncated": is_truncated}
        if not (body.endpoint_url or "").strip() or not (body.bucket_name or "").strip():
            raise ValueError("Для S3 укажите endpoint и имя бакета")
        client = _remote_s3_client(
            body.endpoint_url,
            body.access_key_id,
            body.secret_access_key,
            body.region,
        )
        kwargs: dict = {"Bucket": body.bucket_name.strip(), "MaxKeys": body.max_keys}
        pre = body.prefix.strip()
        if pre:
            kwargs["Prefix"] = pre
        resp = client.list_objects_v2(**kwargs)
        contents = resp.get("Contents") or []
        objects = [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            }
            for obj in contents
        ]
        return {
            "objects": objects,
            "is_truncated": resp.get("IsTruncated", False),
        }
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        logger.error("remote-s3 list failed: %s", exc, exc_info=True)
        raise HTTPException(502, f"Не удалось прочитать внешний источник: {exc}") from exc


@router.post("/remote-s3/import")
def remote_s3_import(body: RemoteS3ImportRequest, background_tasks: BackgroundTasks):
    filenames = body.keys
    task_id = uuid.uuid4().hex
    prov = (body.provider or "s3").strip().lower()
    oauth = (body.oauth_token or "").strip()
    if (
        prov in ("s3", "")
        and oauth
        and not (body.endpoint_url or "").strip()
        and not (body.bucket_name or "").strip()
    ):
        prov = "yandex_disk"
    if prov in ("google_drive", "google-drive", "gdrive"):
        dest_keys = [
            SOURCE_PREFIX + f"pending-{task_id[:8]}-{i}"
            for i in range(len(filenames))
        ]
    else:
        dest_keys = [source_import_storage_key(k) for k in filenames]
    set_task(task_id, {
        "status": "pending",
        "filename": dest_keys[0] if dest_keys else "",
        "progress": 0,
        "total": 0,
        "batch_index": 0,
        "batch_total": len(filenames),
    })
    if prov in ("yandex_disk", "yandex-disk", "yandex"):
        if not (body.oauth_token or "").strip():
            raise HTTPException(400, "Укажите OAuth-токен Яндекс.Диска")
        background_tasks.add_task(_import_yandex_disk_task, task_id, body.oauth_token, filenames)
    elif prov in ("google_drive", "google-drive", "gdrive"):
        if not (body.oauth_token or "").strip():
            raise HTTPException(400, "Укажите OAuth-токен Google Диска")
        background_tasks.add_task(_import_google_drive_task, task_id, body.oauth_token, filenames)
    else:
        if not (body.endpoint_url or "").strip() or not (body.bucket_name or "").strip():
            raise HTTPException(400, "Для S3 укажите endpoint и имя бакета")
        background_tasks.add_task(
            _import_remote_s3_task,
            task_id,
            body.endpoint_url,
            body.bucket_name.strip(),
            body.access_key_id,
            body.secret_access_key,
            body.region,
            filenames,
        )
    return {"task_id": task_id, "keys": dest_keys}


class DeleteObjectsRequest(BaseModel):
    keys: list[str] = Field(min_length=1, max_length=100)

    @field_validator("keys")
    @classmethod
    def only_managed_prefixes(cls, v: list[str]) -> list[str]:
        cleaned = []
        for raw in v:
            key = (raw or "").strip().replace("\\", "/")
            if not key:
                continue
            if ".." in key.split("/"):
                continue
            if key.startswith(UPLOAD_PREFIX) or key.startswith(SOURCE_PREFIX):
                cleaned.append(key)
        if not cleaned:
            raise ValueError("укажите ключи только с префиксами uploads/ или sources/")
        return cleaned


@router.post("/delete-objects")
def delete_objects(body: DeleteObjectsRequest):
    """Удаление объектов из текущего бакета (только uploads/* и sources/*)."""
    s3 = get_s3()
    bucket = get_bucket()
    deleted: list[str] = []
    errors: list[dict] = []
    for key in body.keys:
        try:
            s3.delete_object(Bucket=bucket, Key=key)
            deleted.append(key)
            logger.info("S3 delete_object OK: bucket=%s key=%s", bucket, key)
        except Exception as exc:
            logger.error(
                "S3 delete_object failed: bucket=%s key=%s: %s",
                bucket,
                key,
                exc,
                exc_info=True,
            )
            errors.append({"key": key, "error": str(exc)})
    return {"deleted": deleted, "errors": errors, "count": len(deleted)}


def _download_object_metadata(filename: str) -> tuple[int, str]:
    """Размер и Content-Type объекта в S3 (как для GET download)."""
    filename = validate_s3_key(filename)
    try:
        head = get_s3().head_object(Bucket=get_bucket(), Key=filename)
    except Exception:
        raise HTTPException(404, "Файл не найден") from None

    total_size = int(head.get("ContentLength", 0) or 0)
    content_type = head.get("ContentType") or "application/octet-stream"

    ext = os.path.splitext(filename)[1].lower()
    video_types = {
        ".mp4": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mkv": "video/x-matroska",
        ".mov": "video/quicktime",
        ".webm": "video/webm",
    }
    if ext in video_types:
        content_type = video_types[ext]

    return total_size, content_type


@router.head("/download/{filename:path}")
def head_download_file(filename: str):
    """HEAD для размера и типа файла (нужно linza-vpleer перед Range-стримом)."""
    total_size, content_type = _download_object_metadata(filename)
    return Response(
        status_code=200,
        headers={
            "Content-Length": str(total_size),
            "Content-Type": content_type,
            "Accept-Ranges": "bytes",
            "Content-Disposition": _safe_content_disposition(filename),
        },
    )


@router.get("/download/{filename:path}")
def download_file(filename: str, request: Request):
    """Потоковая отдача файла из S3 с поддержкой Range requests."""
    total_size, content_type = _download_object_metadata(filename)

    range_header = request.headers.get("range")

    if range_header and total_size:
        if not range_header.startswith("bytes="):
            raise HTTPException(416, "Invalid Range header")
        try:
            range_spec = range_header[6:]  # strip "bytes="
            parts = range_spec.split("-")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if parts[1] else total_size - 1
        except (ValueError, IndexError):
            raise HTTPException(416, "Invalid Range header")
        end = min(end, total_size - 1)
        if start < 0 or start > end or start >= total_size:
            raise HTTPException(416, "Range Not Satisfiable")
        content_length = end - start + 1

        def _range_stream():
            resp = get_s3().get_object(
                Bucket=get_bucket(), Key=filename,
                Range=f"bytes={start}-{end}",
            )
            body = resp["Body"]
            while True:
                chunk = body.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk
            body.close()

        return StreamingResponse(
            _range_stream(),
            status_code=206,
            media_type=content_type,
            headers={
                "Content-Range": f"bytes {start}-{end}/{total_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Disposition": _safe_content_disposition(filename),
            },
        )

    def _stream():
        resp = get_s3().get_object(Bucket=get_bucket(), Key=filename)
        body = resp["Body"]
        while True:
            chunk = body.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk
        body.close()

    return StreamingResponse(
        _stream(),
        media_type=content_type,
        headers={
            "Content-Length": str(total_size),
            "Accept-Ranges": "bytes",
            "Content-Disposition": _safe_content_disposition(filename),
        },
    )


@router.get("/progress/{task_id}")
async def progress_stream(task_id: str):
    async def _stream():
        while True:
            task = get_task(task_id)
            if not task:
                yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
                break
            yield f"data: {json.dumps(task)}\n\n"
            if task.get("status") in ("completed", "error"):
                break
            await asyncio.sleep(0.4)

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
