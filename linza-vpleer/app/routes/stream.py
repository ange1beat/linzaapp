"""Эндпоинты потокового воспроизведения видео."""

import os
import pathlib
import re
from urllib.parse import quote as url_quote

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse, StreamingResponse

from app.config import TEMP_DIR
from app.services.ffmpeg import (
    download_from_storage,
    extract_fragment,
    generate_hls,
    get_stream_info,
)
from app.storage_http import build_storage_download_url, storage_request_headers

router = APIRouter(prefix="/api/vpleer", tags=["stream"])


def _safe_content_disposition(name: str, disposition: str = "inline") -> str:
    """Build Content-Disposition header safe from header injection (RFC 5987)."""
    encoded = url_quote(name, safe="")
    return f"{disposition}; filename*=UTF-8''{encoded}"


async def _storage_object_total_size(
    client: httpx.AsyncClient,
    download_url: str,
    svc_headers: dict[str, str],
) -> int:
    """Размер объекта в storage: HEAD, либо GET Range bytes=0-0 если HEAD не поддерживается (405/501)."""
    head_resp = await client.head(download_url, headers=svc_headers)
    if head_resp.status_code == 200:
        return int(head_resp.headers.get("content-length", 0) or 0)
    if head_resp.status_code in (405, 501):
        async with client.stream(
            "GET",
            download_url,
            headers={**svc_headers, "Range": "bytes=0-0"},
        ) as probe:
            if probe.status_code == 206:
                cr = (probe.headers.get("content-range") or "").strip()
                m = re.match(r"^bytes \d+-\d+/(\d+)$", cr)
                if m:
                    return int(m.group(1))
            if probe.status_code == 200:
                return int(probe.headers.get("content-length", 0) or 0)
        raise HTTPException(
            502,
            "Хранилище не отдало размер файла (HEAD недоступен, Range-проба не удалась)",
        )
    raise HTTPException(head_resp.status_code, "Файл не найден в хранилище")


CONTENT_TYPES = {
    ".mp4": "video/mp4",
    ".m4v": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpeg",
    ".mxf": "application/mxf",
    ".hevc": "video/mp4",
}


def _get_http_client(request: Request) -> httpx.AsyncClient:
    """Получить shared HTTP client или создать новый (fallback для тестов)."""
    client = getattr(getattr(request.app, "state", None), "http_client", None)
    if client is not None:
        return client
    return httpx.AsyncClient(timeout=httpx.Timeout(30, read=3600))


@router.get("/stream/{filename:path}")
async def stream_video(filename: str, request: Request):
    """Потоковое воспроизведение видеофайла из S3-хранилища.

    Поддерживает HTTP Range requests для корректной работы
    тега <video> в браузере (перемотка, прогресс-бар).
    """
    download_url = build_storage_download_url(filename)
    svc_headers = storage_request_headers()

    ext = os.path.splitext(filename)[1].lower()
    content_type = CONTENT_TYPES.get(ext, "video/mp4")

    # Размер: HEAD; если прокси/storage режет HEAD (405) — GET bytes=0-0
    client = _get_http_client(request)
    total_size = await _storage_object_total_size(client, download_url, svc_headers)

    range_header = request.headers.get("range")

    if range_header and total_size:
        # Парсинг Range: bytes=start-end
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

        range_hdrs = {**svc_headers, "Range": f"bytes={start}-{end}"}

        async def _range_stream():
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(10, read=600)
            ) as client:
                async with client.stream(
                    "GET",
                    download_url,
                    headers=range_hdrs,
                ) as resp:
                    async for chunk in resp.aiter_bytes(chunk_size=1024 * 1024):
                        yield chunk

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

    # Полная отдача без Range
    async def _full_stream():
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10, read=600)
        ) as client:
            async with client.stream("GET", download_url, headers=svc_headers) as resp:
                if resp.status_code != 200:
                    raise HTTPException(resp.status_code, "Файл не найден в хранилище")
                async for chunk in resp.aiter_bytes(chunk_size=1024 * 1024):
                    yield chunk

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Disposition": _safe_content_disposition(filename),
    }
    if total_size:
        headers["Content-Length"] = str(total_size)

    return StreamingResponse(
        _full_stream(),
        media_type=content_type,
        headers=headers,
    )


@router.get("/fragment")
async def get_fragment(
    filename: str = Query(..., description="Имя файла в хранилище"),
    start: float = Query(..., ge=0, description="Начало фрагмента (секунды)"),
    end: float = Query(..., gt=0, description="Конец фрагмента (секунды)"),
):
    """Вырезка и воспроизведение фрагмента видео по временному интервалу.

    Скачивает файл из storage-service, вырезает фрагмент с помощью ffmpeg
    и возвращает результат.
    """
    if end <= start:
        raise HTTPException(400, "end должен быть больше start")

    download_url = build_storage_download_url(filename)
    try:
        file_path = await download_from_storage(download_url, filename)
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, "Файл не найден в хранилище")

    try:
        fragment_path = await extract_fragment(file_path, start, end)
    except RuntimeError as e:
        raise HTTPException(500, f"Ошибка извлечения фрагмента: {e}")

    return FileResponse(
        fragment_path,
        media_type="video/mp4",
        filename=f"fragment_{filename}",
        headers={"Content-Disposition": _safe_content_disposition(f"fragment_{filename}")},
    )


# ── B3: Playback info ──

# Форматы, которые браузер может воспроизвести progressive
_PROGRESSIVE_EXTENSIONS = {".mp4", ".m4v", ".webm", ".mov"}
_PROGRESSIVE_CODECS = {"h264", "vp8", "vp9", "av1"}


@router.get("/playback-info/{filename:path}")
async def playback_info(filename: str):
    """Определить стратегию воспроизведения файла: progressive или transcode.

    Вызывает ffprobe по URL для определения кодека и контейнера.
    """
    download_url = build_storage_download_url(filename)
    ext = os.path.splitext(filename)[1].lower()

    info = await get_stream_info(download_url)
    codec = info.get("codec", "")
    audio_codec = info.get("audio_codec", "")
    duration = info.get("duration", 0)
    can_stream_copy = codec == "h264"
    warnings = []

    # Определение стратегии
    if ext in _PROGRESSIVE_EXTENSIONS and codec in _PROGRESSIVE_CODECS:
        strategy = "progressive"
    elif ext in (".avi",):
        strategy = "transcode"
        warnings.append(
            "AVI: индекс в конце файла, seek без транскодирования невозможен."
        )
    elif ext in (".mkv", ".mpeg", ".mpg", ".mxf", ".hevc"):
        strategy = "transcode"
    else:
        strategy = "progressive"

    # Предупреждение для больших файлов при транскодировании
    if strategy == "transcode" and duration > 0 and not can_stream_copy:
        est_minutes = max(1, int(duration / 60 * 0.5))  # ~0.5x realtime ultrafast
        if est_minutes > 5:
            warnings.append(
                f"Транскодирование может занять ~{est_minutes} мин."
            )

    # Формат для UI
    ext_label = ext.lstrip(".").upper()
    codec_label = codec.upper() if codec else "?"
    format_label = f"{ext_label} ({codec_label})"

    stream_url = f"/api/vpleer/stream/{url_quote(filename, safe='/')}"
    hls_url = f"/api/vpleer/hls/{url_quote(filename, safe='/')}/playlist.m3u8"

    return {
        "strategy": strategy,
        "stream_url": stream_url,
        "hls_url": hls_url if strategy == "transcode" else None,
        "needs_transcode": strategy == "transcode",
        "can_stream_copy": can_stream_copy,
        "codec": codec,
        "audio_codec": audio_codec,
        "container": info.get("container", ""),
        "duration": duration,
        "format_label": format_label,
        "warnings": warnings,
    }


# ── B4: HLS on-demand transcoding ──

@router.get("/hls/{filename:path}/playlist.m3u8")
async def hls_playlist(filename: str):
    """Сгенерировать HLS-плейлист для файла (транскодирование on-demand).

    Если сегменты уже закэшированы — возвращает мгновенно.
    """
    download_url = build_storage_download_url(filename)

    # Определить кодек для оптимизации (stream copy для H.264)
    info = await get_stream_info(download_url)

    try:
        playlist_path = await generate_hls(
            download_url, filename,
            codec=info.get("codec", ""),
            audio_codec=info.get("audio_codec", ""),
        )
    except RuntimeError as e:
        raise HTTPException(500, f"Ошибка HLS-транскодирования: {e}")

    return FileResponse(
        playlist_path,
        media_type="application/vnd.apple.mpegurl",
        filename="playlist.m3u8",
    )


@router.get("/hls/{filename:path}/{segment}")
async def hls_segment(filename: str, segment: str):
    """Отдать HLS-сегмент (.ts файл) из кэша."""
    # Валидация имени сегмента для предотвращения directory traversal
    if not re.match(r"^seg_\d{3}\.ts$", segment):
        raise HTTPException(400, "Невалидное имя сегмента")

    safe_name = filename.replace("/", "_").replace("..", "")
    base_path = pathlib.Path(TEMP_DIR, "hls").resolve()
    seg_path = (base_path / safe_name / segment).resolve()
    if not str(seg_path).startswith(str(base_path)):
        raise HTTPException(400, "Невалидный путь")

    if not seg_path.is_file():
        raise HTTPException(404, "Сегмент не найден")

    return FileResponse(seg_path, media_type="video/mp2t")
