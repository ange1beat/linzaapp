"""Эндпоинты метаданных и превью видеофайлов."""

import os

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.services.ffmpeg import (
    download_from_storage,
    extract_thumbnail,
    get_metadata_from_url,
)
from app.storage_http import build_storage_download_url

router = APIRouter(prefix="/api/vpleer", tags=["metadata"])


@router.get("/metadata/{filename:path}")
async def video_metadata(filename: str):
    """Метаданные видеофайла: формат, длительность, разрешение, кодеки."""
    download_url = build_storage_download_url(filename)
    try:
        meta = await get_metadata_from_url(download_url)
    except RuntimeError as e:
        raise HTTPException(500, f"Ошибка получения метаданных: {e}")

    return meta


@router.get("/thumbnail/{filename:path}")
async def video_thumbnail(
    filename: str,
    time: float = Query(1.0, ge=0, description="Время кадра (секунды)"),
):
    """Превью-кадр видеофайла в формате JPEG.

    По умолчанию берётся кадр на 1-й секунде видео.
    Можно указать произвольное время через параметр `time`.
    """
    download_url = build_storage_download_url(filename)
    try:
        file_path = await download_from_storage(download_url, filename)
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, "Файл не найден в хранилище")

    try:
        thumb_path = await extract_thumbnail(file_path, time)
    except RuntimeError as e:
        raise HTTPException(500, f"Ошибка генерации превью: {e}")

    return FileResponse(
        thumb_path,
        media_type="image/jpeg",
        filename=f"thumb_{os.path.splitext(filename)[0]}.jpg",
    )
