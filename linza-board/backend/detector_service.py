"""Клиент внешнего Линза.Детектор (OpenAPI linza.detector-rest-api.yml) и обработка очереди анализа."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from typing import Any
from urllib.parse import quote

import httpx
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import AnalysisReport, VideoAnalysisQueueItem

logger = logging.getLogger("linza.detector")


def _env_int(name: str, default: int) -> int:
    """Как int(os.getenv), но пустая строка в .env не ломает запуск (int('') не вызывается)."""
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    return int(str(raw).strip())


# Классы нарушений по умолчанию (все подклассы из схемы DetectionClass).
DEFAULT_DETECTION_CLASSES: list[dict[str, Any]] = [
    {"class": "DRUGS", "subclasses": ["ALCOHOL", "SMOKING", "DRUGS", "DRUGS2KIDS"]},
    {"class": "DEVIANT", "subclasses": ["VANDALISM", "VIOLENCE", "SUICIDE", "KIDSSUICIDE", "OBSCENE_LANGUAGE"]},
    {"class": "TERRORISM", "subclasses": ["TERROR", "EXTREMISM", "TERRORCONTENT"]},
    {"class": "SEX", "subclasses": ["NUDE", "SEX", "KIDSPORN"]},
    {"class": "ANTITRADITIONAL", "subclasses": ["LGBT", "CHILDFREE"]},
    {"class": "ANTIPATRIOTIC", "subclasses": ["INOAGENT", "INOAGENTCONTENT", "ANTIWAR"]},
    {"class": "LUDOMANIA", "subclasses": ["LUDOMANIA"]},
]


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _fetch_secret_bytes() -> bytes | None:
    s = (os.getenv("DETECTOR_FETCH_SECRET") or os.getenv("AUTH_SECRET_KEY") or "").encode("utf-8")
    return s if s else None


def _fetch_secret() -> bytes:
    b = _fetch_secret_bytes()
    if not b:
        raise ValueError("Задайте DETECTOR_FETCH_SECRET или AUTH_SECRET_KEY для подписи ссылок на видео")
    return b


def make_detector_fetch_token(storage_key: str, ttl_sec: int | None = None) -> str:
    """Подписанный токен: GET /api/detector-fetch?token=… (или /{token} в legacy) отдаёт видео из storage."""
    ttl = ttl_sec if ttl_sec is not None else _env_int("DETECTOR_FETCH_TOKEN_TTL_SEC", 7200)
    secret = _fetch_secret()
    exp = int(time.time()) + ttl
    payload = json.dumps({"k": storage_key, "exp": exp}, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = hmac.new(secret, payload, hashlib.sha256).digest()
    return f"{_b64url(payload)}.{_b64url(sig)}"


def parse_detector_fetch_token(token: str) -> str | None:
    try:
        secret = _fetch_secret_bytes()
        if not secret or "." not in token:
            return None
        pb64, sb64 = token.split(".", 1)
        payload = _b64url_decode(pb64)
        sig = _b64url_decode(sb64)
        if not hmac.compare_digest(hmac.new(secret, payload, hashlib.sha256).digest(), sig):
            return None
        obj = json.loads(payload.decode("utf-8"))
        try:
            exp_val = obj.get("exp", 0)
            exp_i = int(exp_val) if exp_val not in (None, "") else 0
        except (TypeError, ValueError):
            return None
        if exp_i < time.time():
            return None
        key = obj.get("k")
        return key if isinstance(key, str) and key else None
    except Exception:
        return None


def validate_storage_key_for_fetch(key: str) -> str:
    key = (key or "").strip().replace("\\", "/")
    if not key or key.startswith("/") or ".." in key.split("/"):
        raise ValueError("Недопустимый ключ файла")
    if not (key.startswith("uploads/") or key.startswith("sources/")):
        raise ValueError("Доступны только ключи uploads/ и sources/")
    return key


def detector_api_base() -> str:
    return os.getenv("DETECTOR_API_BASE_URL", "").strip().rstrip("/")


def detector_provider() -> str:
    """legacy — внешний Линза.Детектор (JSON job + URL); video_ai_filter — сервис video-ai-filter."""
    v = (os.getenv("DETECTOR_PROVIDER") or "legacy").strip().lower().replace("-", "_")
    if v in ("video_ai_filter", "va_filter", "aifilter"):
        return "video_ai_filter"
    return "legacy"


def _url_looks_local_only(url: str) -> bool:
    u = (url or "").lower()
    return (
        "localhost" in u
        or "127.0.0.1" in u
        or "0.0.0.0" in u
        or "[::1]" in u
    )


def public_fetch_base() -> str:
    """Базовый URL Linza снаружи (nginx / один origin), до которого достучится сервер детектора."""
    for env_key in ("DETECTOR_PUBLIC_FETCH_BASE_URL", "LINZA_PUBLIC_URL"):
        b = os.getenv(env_key, "").strip().rstrip("/")
        if b:
            return b
    # Часто совпадает с адресом фронта в проде; localhost для удалённого детектора не подходит.
    fb = os.getenv("FRONTEND_BASE_URL", "").strip().rstrip("/")
    if fb and not _url_looks_local_only(fb):
        return fb
    return ""


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


def build_source_url(storage_key: str) -> str:
    base = public_fetch_base()
    if not base:
        raise ValueError(
            "Нужен публичный базовый URL вашей Linza (без пути в конце), с которого сервер детектора сможет сделать "
            "GET /api/detector-fetch?token=…. Задайте в окружении board один из вариантов: "
            "DETECTOR_PUBLIC_FETCH_BASE_URL=https://ваш-домен.ru или LINZA_PUBLIC_URL (то же), "
            "либо FRONTEND_BASE_URL без localhost (если это реальный вход пользователей). "
            "Для проверки с ноутбука без белого IP — ngrok/Cloudflare Tunnel на порт nginx (обычно 80)."
        )
    token = make_detector_fetch_token(storage_key)
    # Query ?token= — чтобы внешние загрузчики (yt-dlp) не принимали суффикс подписи за «расширение» файла.
    q = quote(token, safe="")
    return f"{base}/api/detector-fetch?token={q}"


def detection_classes_payload() -> list[dict[str, Any]]:
    raw = os.getenv("DETECTOR_DETECTION_CLASSES_JSON", "").strip()
    if raw:
        return json.loads(raw)
    return list(DEFAULT_DETECTION_CLASSES)


def create_detector_job(storage_key: str, job_id: str) -> None:
    base = detector_api_base()
    if not base:
        raise RuntimeError("Не задан DETECTOR_API_BASE_URL")
    profile = (os.getenv("DETECTOR_PROFILE", "FULL").strip().upper() or "FULL")
    if profile not in ("FULL", "PREVIEW"):
        profile = "FULL"
    body: dict[str, Any] = {
        "jobId": job_id,
        "source": build_source_url(storage_key),
        "profile": profile,
        "detectionClasses": detection_classes_payload(),
    }
    cid = os.getenv("DETECTOR_CUSTOMER_ID", "").strip()
    if cid:
        body["customerId"] = cid
    r = httpx.post(f"{base}/api/jobs", json=body, timeout=120.0)
    if r.status_code not in (200, 201):
        msg = r.text
        try:
            err = r.json().get("error")
            if isinstance(err, dict) and err.get("message"):
                msg = err["message"]
        except Exception:
            pass
        raise RuntimeError(f"Детектор отклонил задачу ({r.status_code}): {msg}")


def fetch_job(job_id: str) -> dict[str, Any]:
    base = detector_api_base()
    r = httpx.get(f"{base}/api/jobs/{job_id}", timeout=120.0)
    if r.status_code == 404:
        raise RuntimeError("Задача не найдена на стороне детектора")
    if r.status_code != 200:
        raise RuntimeError(f"Детектор GET job: HTTP {r.status_code} {r.text[:500]}")
    return r.json()


def wait_for_job(job_id: str) -> dict[str, Any]:
    total_timeout = _env_int("DETECTOR_POLL_TIMEOUT_SEC", 4 * 3600)
    interval = _env_int("DETECTOR_POLL_INTERVAL_SEC", 5)
    deadline = time.time() + total_timeout
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = fetch_job(job_id)
        st = last.get("status")
        if st == "DONE":
            return last
        if st == "ERROR":
            err = last.get("error") or {}
            msg = err.get("message", "ERROR") if isinstance(err, dict) else str(err)
            raise RuntimeError(msg)
        time.sleep(interval)
    raise TimeoutError("Превышено время ожидания ответа детектора")


def _slim_job_payload(raw: dict[str, Any]) -> dict[str, Any]:
    """Strip bulky fields (statusMessage logs, ANSI codes) before persisting to DB.

    Keeps: jobId, status, result (detections, statistics, sourceInfo), request, timestamps.
    Drops: statusMessage (can be megabytes of processing logs with escape codes).
    """
    out = {k: v for k, v in raw.items() if k != "statusMessage"}
    sm = raw.get("statusMessage")
    if isinstance(sm, str) and sm:
        # Keep first 500 chars as a breadcrumb for debugging
        out["statusMessage"] = sm[:500] + ("…" if len(sm) > 500 else "")
    return out


def save_report_from_job(
    db: Session,
    user_id: int | None,
    storage_key: str,
    job_payload: dict[str, Any],
    *,
    report_source: str = "detector-api",
) -> int:
    result = job_payload.get("result") or {}
    detections = result.get("detections")
    if isinstance(detections, list):
        match_count = result.get("totalDetections")
        if match_count is None:
            match_count = len(detections)
    else:
        td = result.get("totalDetections")
        try:
            match_count = int(td) if td not in (None, "") else 0
        except (TypeError, ValueError):
            match_count = 0
    jid = job_payload.get("jobId", "")
    slim = _slim_job_payload(job_payload)
    src_label = report_source if report_source else "detector-api"
    prefix = "detector" if src_label == "detector-api" else "vaf"
    report = AnalysisReport(
        filename=storage_key,
        report_name=f"{prefix}-{jid}.json" if jid else f"{prefix}-job.json",
        source=src_label,
        started_at=result.get("startedAt", ""),
        finished_at=result.get("finishedAt", ""),
        match_count=match_count,
        status="success",
        report_json=json.dumps(slim, ensure_ascii=False),
        created_by=user_id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report.id


def is_queue_item_cancelled(item_id: int) -> bool:
    """Отдельная сессия — видит commit из DELETE очереди в другом запросе."""
    db = SessionLocal()
    try:
        row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
        return row is None or row.status == "cancelled"
    finally:
        db.close()


def process_analysis_queue_item(item_id: int) -> None:
    """Фоновая обработка одной записи очереди (sync, для BackgroundTasks)."""
    from backend import video_ai_filter_client

    db = SessionLocal()
    try:
        row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
        if not row or row.status != "pending":
            return

        if detector_provider() == "video_ai_filter":
            if not video_ai_filter_client.api_base():
                row.status = "error"
                row.error_message = "Не задан VIDEO_AI_FILTER_BASE_URL (URL сервиса video-ai-filter)."
                db.commit()
                return
            try:
                validate_storage_key_for_fetch(row.storage_key)
            except ValueError as e:
                row.status = "error"
                row.error_message = str(e)
                db.commit()
                return

            row.status = "processing"
            row.detector_job_id = "preparing"
            row.error_message = None
            db.commit()

            cancel_ck = lambda: is_queue_item_cancelled(item_id)
            try:
                vaf_jid = video_ai_filter_client.submit_job_from_storage(
                    row.storage_key,
                    cancel_check=cancel_ck,
                )
                row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
                if not row or row.status != "processing":
                    logger.info(
                        "Запись очереди %s снята до опроса video-ai-filter — пропуск",
                        item_id,
                    )
                    return
                row.detector_job_id = str(vaf_jid)[:500]
                db.commit()

                job_payload = video_ai_filter_client.wait_job_export(vaf_jid, cancel_check=cancel_ck)
                row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
                if not row or row.status != "processing":
                    logger.info(
                        "Запись очереди %s снята до сохранения отчёта — результат video-ai-filter отброшен",
                        item_id,
                    )
                    return
                rid = save_report_from_job(
                    db,
                    row.created_by,
                    row.storage_key,
                    job_payload,
                    report_source="video-ai-filter",
                )
                row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
                if row and row.status == "processing":
                    row.status = "done"
                    row.report_id = rid
                    row.error_message = None
                    db.commit()
            except video_ai_filter_client.QueueCancelled:
                logger.info("Анализ очереди id=%s остановлен (снято с очереди)", item_id)
                return
            except Exception as e:
                logger.exception("Ошибка анализа очереди (video-ai-filter) id=%s", item_id)
                if is_queue_item_cancelled(item_id):
                    return
                row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
                if row:
                    row.status = "error"
                    row.error_message = str(e)[:4000]
                    db.commit()
            return

        if not detector_api_base():
            row.status = "error"
            row.error_message = "Не задан DETECTOR_API_BASE_URL (URL API Линза.Детектор)."
            db.commit()
            return

        try:
            build_source_url(row.storage_key)
        except ValueError as e:
            row.status = "error"
            row.error_message = str(e)
            db.commit()
            return

        job_id = str(uuid.uuid4())
        row.status = "processing"
        row.detector_job_id = job_id
        row.error_message = None
        db.commit()

        try:
            create_detector_job(row.storage_key, job_id)
            job_payload = wait_for_job(job_id)
            row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
            if not row or row.status != "processing":
                logger.info("Запись очереди %s снята до сохранения отчёта — результат детектора отброшен", item_id)
                return
            rid = save_report_from_job(db, row.created_by, row.storage_key, job_payload)
            row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
            if row and row.status == "processing":
                row.status = "done"
                row.report_id = rid
                row.error_message = None
                db.commit()
        except Exception as e:
            logger.exception("Ошибка анализа очереди id=%s", item_id)
            row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
            if row:
                row.status = "error"
                row.error_message = str(e)[:4000]
                db.commit()
    finally:
        db.close()
