"""Эндпоинт временной шкалы нарушений для визуализации в плеере."""

from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.config import ANALYTICS_SERVICE_URL

router = APIRouter(prefix="/api/vpleer", tags=["timeline"])


CATEGORY_COLORS = {
    "prohibited": "#dc3545",
    "18+": "#fd7e14",
    "16+": "#ffc107",
}

SOURCE_COLORS = {
    "video": "#53c0f0",
    "audio": "#a855f7",
    "both": "#ec4899",
}


async def _fetch_classifier_config() -> list[dict[str, Any]]:
    """Классификатор в analytics зарегистрирован как GET /api/classifier/ — без слэша даёт 307, httpx по умолчанию редиректы не ходит."""
    url = f"{ANALYTICS_SERVICE_URL.rstrip('/')}/api/classifier/"
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else []
    except (httpx.HTTPError, ValueError, TypeError):
        raise HTTPException(502, "Не удалось получить конфигурацию классификатора")


async def _fetch_classifier_config_safe() -> list[dict[str, Any]]:
    """Как _fetch_classifier_config, но без 502 — плеер должен показывать маркеры даже без linza-analytics в Docker."""
    try:
        return await _fetch_classifier_config()
    except HTTPException:
        return []


def _category_map(classifier_config: list[dict[str, Any]]) -> dict[str, str]:
    return {
        item.get("subclass", ""): item.get("category", "16+")
        for item in classifier_config
    }


def _coerce_time(det: dict[str, Any], key: str, fallback_key: str) -> Any:
    """Return human-readable time, falling back to seconds from detector API."""
    val = det.get(key)
    if val not in (None, ""):
        return val
    sec = det.get(fallback_key)
    if sec is not None:
        return float(sec)
    return ""


def _vaf_subclass_and_source(det: dict[str, Any]) -> tuple[str, str]:
    """TIME_BASED_REPORT от video-ai-filter: subclass — код нарушения; type часто 'audio'|'video' (модальность), не подкласс."""
    raw_sub = det.get("subclass")
    subclass = str(raw_sub).strip() if raw_sub not in (None, "") else ""
    if not subclass:
        t = det.get("type")
        if isinstance(t, str) and t.lower() not in ("audio", "video", "both"):
            subclass = t.strip()
        else:
            subclass = ""
    src_raw = det.get("source") or det.get("modality")
    if isinstance(src_raw, str) and src_raw.strip():
        sl = src_raw.strip().lower()
        if sl in ("video", "audio", "both"):
            source = sl
        elif src_raw.strip().upper() == "VIDEO":
            source = "video"
        elif src_raw.strip().upper() == "AUDIO":
            source = "audio"
        else:
            source = "both"
    else:
        t2 = det.get("type")
        if isinstance(t2, str) and t2.lower() in ("audio", "video"):
            source = t2.lower()
        else:
            source = "both"
    return subclass, source


def _markers_from_items(
    category_map: dict[str, str],
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    markers = []
    for idx, det in enumerate(items):
        subclass, source = _vaf_subclass_and_source(det)
        category = category_map.get(subclass, "16+")
        markers.append({
            "id": det.get("id") or f"det_{idx}",
            "subclass": subclass,
            "category": category,
            "color": CATEGORY_COLORS.get(category, "#ffc107"),
            "start_time": _coerce_time(det, "start_time", "startSeconds"),
            "end_time": _coerce_time(det, "end_time", "endSeconds"),
            "confidence": det.get("confidence"),
            "source": source,
        })
    return markers


async def _timeline_with_detections(filename: str, items: list[dict[str, Any]]) -> dict:
    classifier_config = await _fetch_classifier_config_safe()
    cmap = _category_map(classifier_config)
    markers = _markers_from_items(cmap, items)
    return {
        "filename": filename,
        "markers": markers,
        "categories": CATEGORY_COLORS,
        "source_colors": SOURCE_COLORS,
    }


async def _timeline_without_detections(filename: str) -> dict:
    classifier_config = await _fetch_classifier_config_safe()
    return {
        "filename": filename,
        "markers": [],
        "categories": CATEGORY_COLORS,
        "source_colors": SOURCE_COLORS,
        "classifier": classifier_config,
    }


class TimelinePostBody(BaseModel):
    filename: str = Field(..., description="Ключ файла в хранилище")
    detections: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Массив детекций из отчёта",
    )


@router.get("/timeline")
async def violations_timeline(
    filename: str = Query(..., description="Имя анализируемого файла"),
    detections: str = Query(
        None, description="JSON-массив детекций (если передаётся с клиента)"
    ),
):
    """Временная шкала нарушений для наложения на видеоплеер.

    Получает конфигурацию классификатора из linza-analytics
    и возвращает массив маркеров с цветовой кодировкой для визуализации.

    Детекции передаются с фронтенда (т.к. они загружаются как JSON-отчёт).
    Сервис обогащает их категориями и цветами из классификатора.
    """
    if detections:
        try:
            items = json.loads(detections)
        except json.JSONDecodeError:
            raise HTTPException(400, "Невалидный JSON в параметре detections")
        if not isinstance(items, list):
            raise HTTPException(400, "Параметр detections должен быть JSON-массивом")
        row_items: list[dict[str, Any]] = [x for x in items if isinstance(x, dict)]
        return await _timeline_with_detections(filename, row_items)

    return await _timeline_without_detections(filename)


@router.post("/timeline")
async def violations_timeline_post(body: TimelinePostBody):
    """То же обогащение детекций, что и GET, но тело запроса — для больших отчётов."""
    return await _timeline_with_detections(body.filename, body.detections)
