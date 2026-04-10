"""Обёртка над ffmpeg / ffprobe для работы с видео."""

import asyncio
import json
import os
import shutil
import tempfile

import httpx

from app.config import (
    FFMPEG_FRAGMENT_TIMEOUT,
    FFMPEG_HLS_TIMEOUT,
    FFMPEG_THUMBNAIL_TIMEOUT,
    FFPROBE_TIMEOUT,
    SERVICE_API_KEY,
    TEMP_DIR,
)

os.makedirs(TEMP_DIR, exist_ok=True)


def _ffmpeg_http_headers_args(url: str) -> list[str]:
    """Для HTTP(S) источников: передать X-Service-Key в ffmpeg/ffprobe."""
    key = (SERVICE_API_KEY or "").strip()
    if not key or not (url.startswith("http://") or url.startswith("https://")):
        return []
    return ["-headers", f"X-Service-Key: {key}\r\n"]


async def get_metadata(file_path: str) -> dict:
    """Получить метаданные видеофайла через ffprobe."""
    return await _run_ffprobe(file_path)


async def get_metadata_from_url(url: str, timeout: float = FFPROBE_TIMEOUT) -> dict:
    """Получить метаданные видео по URL (без скачивания файла).

    ffprobe сам выполняет HTTP Range-запросы и читает только заголовки/индекс.
    Для AVI (индекс в конце): может зависнуть — используется таймаут.
    """
    try:
        return await asyncio.wait_for(_run_ffprobe(url), timeout=timeout)
    except asyncio.TimeoutError:
        # AVI и другие форматы с индексом в конце — ffprobe может зависнуть
        return {
            "filename": os.path.basename(url.split("?")[0]),
            "format": "", "duration": 0, "duration_formatted": "—",
            "size": 0, "bit_rate": 0,
            "video": {"codec": "", "width": None, "height": None, "fps": 0, "total_frames": 0},
            "audio": {"codec": "", "sample_rate": 0, "channels": None},
            "warning": "Не удалось получить метаданные по URL (таймаут). "
                       "Возможно, индекс файла в конце (AVI).",
        }


async def get_stream_info(url: str, timeout: float = FFPROBE_TIMEOUT) -> dict:
    """Определить кодек, контейнер и возможность stream copy для файла по URL."""
    try:
        data = await asyncio.wait_for(_run_ffprobe_raw(url), timeout=timeout)
    except (asyncio.TimeoutError, RuntimeError):
        ext = os.path.splitext(url.split("?")[0])[1].lower()
        return {
            "codec": "", "audio_codec": "",
            "container": ext.lstrip("."),
            "width": None, "height": None,
            "duration": 0,
            "probed": False,
        }

    fmt = data.get("format", {})
    video_stream = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "video"), {}
    )
    audio_stream = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {}
    )
    ext = os.path.splitext(url.split("?")[0])[1].lower()
    return {
        "codec": video_stream.get("codec_name", ""),
        "audio_codec": audio_stream.get("codec_name", ""),
        "container": ext.lstrip(".") or fmt.get("format_name", ""),
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "duration": float(fmt.get("duration", 0)),
        "probed": True,
    }


async def _run_ffprobe_raw(source: str) -> dict:
    """Запустить ffprobe и вернуть сырой JSON."""
    cmd = [
        "ffprobe", "-v", "quiet",
        *_ffmpeg_http_headers_args(source),
        "-print_format", "json",
        "-show_format", "-show_streams",
        source,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe error: {stderr.decode()}")
    try:
        return json.loads(stdout.decode())
    except json.JSONDecodeError as e:
        raise RuntimeError(f"ffprobe returned invalid JSON: {e}")


async def _run_ffprobe(source: str) -> dict:
    """Запустить ffprobe и вернуть структурированные метаданные."""
    data = await _run_ffprobe_raw(source)

    fmt = data.get("format", {})
    video_stream = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "video"), {}
    )
    audio_stream = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {}
    )

    duration = float(fmt.get("duration", 0))
    return {
        "filename": os.path.basename(fmt.get("filename", "")),
        "format": fmt.get("format_long_name", ""),
        "duration": duration,
        "duration_formatted": _format_time(duration),
        "size": int(fmt.get("size", 0)),
        "bit_rate": int(fmt.get("bit_rate", 0)),
        "video": {
            "codec": video_stream.get("codec_name", ""),
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
            "fps": _parse_fps(video_stream.get("r_frame_rate", "")),
            "total_frames": int(video_stream.get("nb_frames", 0) or 0),
        },
        "audio": {
            "codec": audio_stream.get("codec_name", ""),
            "sample_rate": int(audio_stream.get("sample_rate", 0) or 0),
            "channels": audio_stream.get("channels"),
        },
    }


async def extract_thumbnail(file_path: str, time_sec: float = 1.0) -> str:
    """Извлечь кадр из видео в формате JPEG."""
    out_path = tempfile.mktemp(suffix=".jpg", dir=TEMP_DIR)
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(time_sec),
        "-i", file_path,
        "-frames:v", "1",
        "-q:v", "3",
        out_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        _, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=FFMPEG_THUMBNAIL_TIMEOUT
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        if os.path.exists(out_path):
            os.unlink(out_path)
        raise RuntimeError(
            f"ffmpeg thumbnail timeout ({FFMPEG_THUMBNAIL_TIMEOUT}s)"
        )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg thumbnail error: {stderr.decode()}")
    return out_path


async def extract_fragment(
    file_path: str, start_time: float, end_time: float
) -> str:
    """Вырезать фрагмент видео по временному интервалу."""
    out_path = tempfile.mktemp(suffix=".mp4", dir=TEMP_DIR)
    duration = end_time - start_time
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-i", file_path,
        "-t", str(duration),
        "-c", "copy",
        "-movflags", "+faststart",
        out_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        _, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=FFMPEG_FRAGMENT_TIMEOUT
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        if os.path.exists(out_path):
            os.unlink(out_path)
        raise RuntimeError(
            f"ffmpeg fragment timeout ({FFMPEG_FRAGMENT_TIMEOUT}s)"
        )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg fragment error: {stderr.decode()}")
    return out_path


async def generate_hls(url: str, filename: str, codec: str = "",
                       audio_codec: str = "") -> str:
    """Транскодировать видео в HLS-сегменты. Возвращает путь к .m3u8.

    Если исходный кодек H.264 — используется stream copy (мгновенно).
    Для остальных — ultrafast перекодирование.
    """
    safe_name = filename.replace("/", "_").replace("..", "")
    hls_dir = os.path.join(TEMP_DIR, "hls", safe_name)
    playlist = os.path.join(hls_dir, "playlist.m3u8")
    if os.path.exists(playlist):
        return playlist
    os.makedirs(hls_dir, exist_ok=True)

    # Whitelist кодеков для stream copy
    _copy_video_codecs = {"h264"}
    _copy_audio_codecs = {"aac"}

    if codec in _copy_video_codecs:
        video_flags = ["-c:v", "copy"]
    else:
        video_flags = ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "23"]

    if audio_codec in _copy_audio_codecs:
        audio_flags = ["-c:a", "copy"]
    else:
        audio_flags = ["-c:a", "aac", "-b:a", "128k"]

    cmd = [
        "ffmpeg", "-y",
        *_ffmpeg_http_headers_args(url),
        "-seekable", "1", "-multiple_requests", "1",
        "-i", url,
        *video_flags, *audio_flags,
        "-f", "hls", "-hls_time", "6", "-hls_list_size", "0",
        "-hls_segment_filename", os.path.join(hls_dir, "seg_%03d.ts"),
        playlist,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        _, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=FFMPEG_HLS_TIMEOUT
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        shutil.rmtree(hls_dir, ignore_errors=True)
        raise RuntimeError(
            f"ffmpeg HLS timeout ({FFMPEG_HLS_TIMEOUT}s)"
        )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg HLS error: {stderr.decode()[-500:]}")
    return playlist


async def download_from_storage(url: str, filename: str) -> str:
    """Скачать файл из storage-service во временную директорию."""
    from app.storage_http import storage_request_headers

    file_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(file_path):
        return file_path
    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    h = storage_request_headers()
    async with httpx.AsyncClient(timeout=httpx.Timeout(10, read=600)) as client:
        async with client.stream("GET", url, headers=h) as resp:
            resp.raise_for_status()
            with open(file_path, "wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=1024 * 1024):
                    f.write(chunk)
    return file_path


def _format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:05.2f}"
    return f"{m}:{s:05.2f}"


def _parse_fps(r_frame_rate: str) -> float:
    if "/" in r_frame_rate:
        num, den = r_frame_rate.split("/")
        den_val = int(den)
        if den_val == 0:
            return 0.0
        return round(int(num) / den_val, 2)
    try:
        return float(r_frame_rate)
    except (ValueError, TypeError):
        return 0.0
