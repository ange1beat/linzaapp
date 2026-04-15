"""Клиент сервиса video-ai-filter: скачивание видео из storage, POST /jobs, опрос, экспорт time-based JSON.

Формат отчёта приводится к виду, совместимому с save_report_from_job() и фронтом (поле result.detections).
"""

from __future__ import annotations

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin

import httpx

logger = logging.getLogger("linza.video_ai_filter")


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    return int(str(raw).strip())


def _svc_headers() -> dict[str, str]:
    k = os.getenv("SERVICE_API_KEY", "").strip()
    return {"X-Service-Key": k} if k else {}


def _storage_base() -> str:
    raw = os.getenv("STORAGE_SERVICE_URL", "").strip()
    if raw:
        return raw.rstrip("/")
    if os.path.exists("/.dockerenv"):
        return "http://storage-service:8001"
    return "http://127.0.0.1:8001"


def encode_download_path(key: str) -> str:
    return "/".join(quote(part, safe="") for part in key.split("/"))


def validate_storage_key_for_fetch(key: str) -> str:
    key = (key or "").strip().replace("\\", "/")
    if not key or key.startswith("/") or ".." in key.split("/"):
        raise ValueError("Недопустимый ключ файла")
    if not (key.startswith("uploads/") or key.startswith("sources/")):
        raise ValueError("Доступны только ключи uploads/ и sources/")
    return key


def api_base() -> str:
    return os.getenv("VIDEO_AI_FILTER_BASE_URL", "").strip().rstrip("/")


def _optional_form_int(name: str) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _optional_form_float(name: str) -> float | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _download_storage_file_to_path(storage_key: str, dest: Path) -> None:
    url = f"{_storage_base()}/api/files/download/{encode_download_path(storage_key)}"
    headers = _svc_headers()
    with httpx.stream("GET", url, headers=headers, timeout=httpx.Timeout(600.0, connect=60.0)) as r:
        r.raise_for_status()
        with open(dest, "wb") as out:
            for chunk in r.iter_bytes():
                if chunk:
                    out.write(chunk)


def _post_job(local_path: Path, original_name: str) -> str:
    base = api_base()
    if not base:
        raise RuntimeError("Не задан VIDEO_AI_FILTER_BASE_URL")

    data: dict[str, Any] = {}
    mf = _optional_form_int("VIDEO_AI_FILTER_MAX_FRAMES")
    if mf is not None:
        data["max_frames"] = str(mf)
    md = _optional_form_float("VIDEO_AI_FILTER_MAX_DURATION_SEC")
    if md is not None:
        data["max_duration_sec"] = str(md)
    cats = os.getenv("VIDEO_AI_FILTER_CATEGORIES_JSON", "").strip()
    if cats:
        data["categories_json"] = cats

    mime = "video/mp4"
    suf = Path(original_name).suffix.lower()
    if suf == ".webm":
        mime = "video/webm"
    elif suf in (".mov",):
        mime = "video/quicktime"
    elif suf in (".mkv",):
        mime = "video/x-matroska"

    url = f"{base}/jobs"
    with open(local_path, "rb") as f:
        files = {"file": (Path(original_name).name or "video.mp4", f, mime)}
        r = httpx.post(url, data=data, files=files, timeout=httpx.Timeout(600.0, connect=120.0))

    if r.status_code not in (200, 201):
        msg = r.text[:2000]
        try:
            d = r.json()
            if isinstance(d, dict) and d.get("detail"):
                msg = str(d["detail"])
        except Exception:
            pass
        raise RuntimeError(f"video-ai-filter отклонил задачу ({r.status_code}): {msg}")

    body = r.json()
    job_id = body.get("job_id") or body.get("jobId")
    if not job_id:
        raise RuntimeError("video-ai-filter: в ответе нет job_id")
    return str(job_id)


def _poll_and_fetch_export(job_id: str) -> dict[str, Any]:
    base = api_base()
    interval = _env_int("DETECTOR_POLL_INTERVAL_SEC", 5)
    total_timeout = _env_int("DETECTOR_POLL_TIMEOUT_SEC", 4 * 3600)
    deadline = time.time() + total_timeout

    status_url = f"{base}/jobs/{job_id}"
    while time.time() < deadline:
        r = httpx.get(status_url, timeout=120.0)
        if r.status_code == 404:
            raise RuntimeError("Задача video-ai-filter не найдена")
        if r.status_code != 200:
            raise RuntimeError(f"video-ai-filter GET job: HTTP {r.status_code} {r.text[:500]}")
        row = r.json()
        st = (row.get("status") or "").strip().lower()
        if st == "completed":
            export_path = row.get("export_url") or f"/jobs/{job_id}/export"
            export_url = urljoin(base + "/", export_path.lstrip("/"))
            er = httpx.get(
                export_url,
                params={"format": "time-based", "attachment": "false"},
                timeout=httpx.Timeout(300.0, connect=60.0),
            )
            if er.status_code != 200:
                raise RuntimeError(f"video-ai-filter export: HTTP {er.status_code} {er.text[:500]}")
            return er.json()
        if st == "failed":
            err = row.get("error") or "failed"
            raise RuntimeError(str(err)[:4000])
        time.sleep(interval)

    raise TimeoutError("Превышено время ожидания video-ai-filter")


def _normalize_export_to_job_payload(export_obj: dict[str, Any], job_id: str) -> dict[str, Any]:
    """Привести TIME_BASED_REPORT к форме, ожидаемой save_report_from_job и extractDetectionsPayload на фронте."""
    detections = export_obj.get("detections")
    if not isinstance(detections, list):
        detections = []
    si = export_obj.get("source_info") or export_obj.get("sourceInfo") or {}
    frame_count = si.get("frameCount") or si.get("frame_count")
    fps = si.get("fps") or 0.0
    source_info_ui = {
        "frameCount": int(frame_count) if frame_count not in (None, "") else 0,
        "fps": float(fps) if fps not in (None, "") else 0.0,
    }
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return {
        "jobId": job_id,
        "status": "DONE",
        "result": {
            "detections": detections,
            "totalDetections": len(detections),
            "sourceInfo": source_info_ui,
            "startedAt": "",
            "finishedAt": finished,
        },
    }


def submit_job_from_storage(storage_key: str) -> str:
    """Скачать файл из storage и создать задачу в video-ai-filter. Возвращает UUID job_id (до опроса результата)."""
    key = validate_storage_key_for_fetch(storage_key)
    suffix = Path(key).suffix or ".mp4"
    tmp: Path | None = None
    try:
        fd, tmp_name = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        tmp = Path(tmp_name)
        logger.info("video-ai-filter: downloading %s from storage", key)
        _download_storage_file_to_path(key, tmp)
        display_name = Path(key).name or f"video{suffix}"
        vaf_job_id = _post_job(tmp, display_name)
        logger.info("video-ai-filter: job %s submitted", vaf_job_id)
        return str(vaf_job_id)
    finally:
        if tmp is not None:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass


def wait_job_export(vaf_job_id: str) -> dict[str, Any]:
    """Дождаться завершения задачи и вернуть payload для save_report_from_job."""
    export_obj = _poll_and_fetch_export(vaf_job_id)
    return _normalize_export_to_job_payload(export_obj, vaf_job_id)


def run_pipeline(storage_key: str) -> dict[str, Any]:
    """Скачать файл из storage → отправить в video-ai-filter → вернуть payload для save_report_from_job."""
    jid = submit_job_from_storage(storage_key)
    return wait_job_export(jid)


def fetch_job_pdf_bytes(job_id: str) -> bytes:
    """Скачать PDF-отчёт из video-ai-filter (тот же, что GET /jobs/{id}/export?format=pdf)."""
    base = api_base()
    if not base:
        raise RuntimeError("Не задан VIDEO_AI_FILTER_BASE_URL")
    jid = (job_id or "").strip()
    if not jid:
        raise ValueError("Пустой job_id")
    url = f"{base}/jobs/{jid}/export"
    r = httpx.get(
        url,
        params={"format": "pdf"},
        timeout=httpx.Timeout(300.0, connect=60.0),
    )
    if r.status_code != 200:
        msg = r.text[:800] if r.text else ""
        raise RuntimeError(f"video-ai-filter PDF: HTTP {r.status_code} {msg}")
    data = r.content
    if not data or not data.startswith(b"%PDF"):
        raise RuntimeError("video-ai-filter вернул не PDF (ожидался %PDF)")
    return data


def fetch_job_status_snapshot(job_id: str) -> dict[str, Any] | None:
    """GET /jobs/{id} у video-ai-filter — для строки статуса в очереди board."""
    base = api_base()
    if not base or not job_id or len(job_id) < 32:
        return None
    try:
        r = httpx.get(f"{base}/jobs/{job_id}", timeout=15.0)
        if r.status_code != 200:
            return None
        row = r.json()
    except Exception:
        logger.debug("video-ai-filter: snapshot failed for %s", job_id, exc_info=True)
        return None

    st = (row.get("status") or "").strip().lower()
    fd = int(row.get("frames_done") or 0)
    raw_ft = row.get("frames_total")
    try:
        ft = int(raw_ft) if raw_ft is not None and str(raw_ft).strip() != "" else None
    except (TypeError, ValueError):
        ft = None

    detail = ""
    if st in ("queued", "pending"):
        detail = "В очереди обработчика"
    elif st == "failed":
        detail = (row.get("error") or "Ошибка обработки")[:300]
    elif st == "processing":
        if ft is not None and ft > 0:
            if fd < ft:
                detail = f"Кадры: {fd}/{ft}"
            else:
                detail = "Транскрибация и модерация аудио…"
        else:
            detail = "Обработка видео…"
    elif st == "completed":
        detail = "Завершение…"

    return {
        "vaf_status": st,
        "frames_done": fd,
        "frames_total": ft,
        "progress": row.get("progress"),
        "status_detail": detail,
    }
