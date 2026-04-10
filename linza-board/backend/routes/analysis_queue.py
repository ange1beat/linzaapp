"""Очередь видео на анализ: постановка задач и фоновый вызов внешнего API Линза.Детектор.

Требуются переменные окружения:
- DETECTOR_API_BASE_URL — например http://linza-detect.sociallab.ru:38080
- DETECTOR_PUBLIC_FETCH_BASE_URL — внешний базовый URL вашей Linza (HTTPS), чтобы детектор скачал файл по /api/detector-fetch?token=…
- DETECTOR_FETCH_SECRET или AUTH_SECRET_KEY — подпись временных ссылок на видео
"""

import re
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend import video_ai_filter_client
from backend.auth import get_current_user
from backend.database import get_db
from backend.detector_service import detector_api_base, detector_provider, process_analysis_queue_item
from backend.models import User, VideoAnalysisQueueItem

router = APIRouter()

_QUEUE_LIST_LIMIT = 100


def _dt_iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


class QueueAddRequest(BaseModel):
    storage_keys: list[str] = Field(min_length=1, max_length=200)


def _queue_item_dict(r: VideoAnalysisQueueItem) -> dict:
    return {
        "id": r.id,
        "storage_key": r.storage_key,
        "origin": r.origin,
        "status": r.status,
        "detector_job_id": r.detector_job_id,
        "report_id": r.report_id,
        "error_message": r.error_message,
        "created_at": _dt_iso(r.created_at),
    }


_VAF_JOB_UUID = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _enrich_queue_item_for_ui(d: dict) -> dict:
    """Для DETECTOR_PROVIDER=video_ai_filter — текст прогресса из GET video-ai-filter /jobs/{id}."""
    if detector_provider() != "video_ai_filter":
        return d
    st = d.get("status")
    jid = (d.get("detector_job_id") or "").strip()

    if st == "pending":
        d["status_detail"] = "Ожидает запуска"
        return d
    if st != "processing":
        return d

    if jid == "preparing" or not jid:
        d["status_detail"] = "Подготовка: загрузка файла и отправка в обработчик…"
        return d

    if not _VAF_JOB_UUID.match(jid):
        d["status_detail"] = "Обработка…"
        return d

    snap = video_ai_filter_client.fetch_job_status_snapshot(jid)
    if snap and (snap.get("status_detail") or "").strip():
        d["status_detail"] = (snap.get("status_detail") or "").strip()
        d["vaf_progress"] = {
            "frames_done": snap.get("frames_done"),
            "frames_total": snap.get("frames_total"),
            "progress": snap.get("progress"),
            "vaf_status": snap.get("vaf_status"),
        }
    else:
        d["status_detail"] = "Обработка…"
    return d


@router.get("", include_in_schema=False)
@router.get("/")
def list_queue(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Активные и недавние задачи (кроме отменённых)."""
    q = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.status != "cancelled")
    q = q.order_by(desc(VideoAnalysisQueueItem.id)).limit(_QUEUE_LIST_LIMIT)
    rows = q.all()
    return [_enrich_queue_item_for_ui(_queue_item_dict(r)) for r in rows]


@router.post("", include_in_schema=False)
@router.post("/")
def add_to_queue(
    body: QueueAddRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if detector_provider() == "video_ai_filter":
        if not video_ai_filter_client.api_base():
            raise HTTPException(
                status_code=503,
                detail=(
                    "Анализ через video-ai-filter не настроен: задайте VIDEO_AI_FILTER_BASE_URL "
                    "на сервере board (в Docker обычно http://video-ai-filter:8000)."
                ),
            )
    elif not detector_api_base():
        raise HTTPException(
            status_code=503,
            detail="Анализ через API детектора не настроен: задайте DETECTOR_API_BASE_URL на сервере board.",
        )
    added_ids: list[int] = []
    for raw in body.storage_keys:
        key = (raw or "").strip()
        if not key:
            continue
        exists = (
            db.query(VideoAnalysisQueueItem)
            .filter(
                VideoAnalysisQueueItem.storage_key == key,
                VideoAnalysisQueueItem.status.in_(("pending", "processing")),
            )
            .first()
        )
        if exists:
            continue
        origin = "source" if key.startswith("sources/") else "upload"
        row = VideoAnalysisQueueItem(
            storage_key=key,
            origin=origin,
            status="pending",
            created_by=current_user.id,
        )
        db.add(row)
        db.flush()
        added_ids.append(row.id)
    db.commit()

    for item_id in added_ids:
        background_tasks.add_task(process_analysis_queue_item, item_id)

    return {"added_ids": added_ids, "count": len(added_ids)}


@router.delete("/{item_id}")
def remove_from_queue(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(VideoAnalysisQueueItem).filter(VideoAnalysisQueueItem.id == item_id).first()
    if not row:
        raise HTTPException(404, "Not found")
    row.status = "cancelled"
    db.commit()
    return {"status": "ok"}
