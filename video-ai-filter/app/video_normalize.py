"""Прогрессивный H.264 для OpenCV: interlaced yuv420p ломает swscale при выводе в BGR."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from app.config import Settings

logger = logging.getLogger(__name__)

# field_order из ffprobe для чересстрочного изображения
_INTERLACED_FIELD_ORDERS = frozenset({"tt", "tb", "bt", "bb"})


def probe_field_order(src: Path, ffprobe_bin: str) -> str | None:
    cmd = [
        ffprobe_bin,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=field_order",
        "-of",
        "json",
        str(src),
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        logger.error("ffprobe не найден (%s)", ffprobe_bin)
        return None
    except subprocess.TimeoutExpired:
        logger.warning("ffprobe timeout для %s", src)
        return None
    if proc.returncode != 0:
        logger.warning("ffprobe rc=%s: %s", proc.returncode, (proc.stderr or "")[:400])
        return None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    streams = data.get("streams") or []
    if not streams:
        return None
    fo = streams[0].get("field_order")
    if fo is None:
        return None
    s = str(fo).strip().lower()
    return s or None


def should_normalize_video(src: Path, settings: Settings) -> bool:
    mode = (settings.video_ffmpeg_normalize or "auto").strip().lower()
    if mode == "never":
        return False
    if mode == "always":
        logger.info("VIDEO_FFMPEG_NORMALIZE=always — нормализация перед OpenCV: %s", src.name)
        return True
    fo = probe_field_order(src, settings.ffprobe_path)
    if fo is None:
        return False
    if fo in _INTERLACED_FIELD_ORDERS:
        logger.info("field_order=%s — ffmpeg-нормализация для OpenCV: %s", fo, src.name)
        return True
    return False


def ffmpeg_normalize_for_opencv(
    src: Path,
    dst: Path,
    settings: Settings,
    duration_limit_sec: float | None = None,
) -> None:
    """Деинтерлейс (только помеченные interlaced кадры) → progressive yuv420p, без аудио."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd: list[str] = [
        settings.ffmpeg_path,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(src),
    ]
    if duration_limit_sec is not None and duration_limit_sec > 0:
        cmd.extend(["-t", f"{duration_limit_sec:.3f}"])
    # 0:-1:1 = send_frame, auto parity, deinterlace только interlaced (progressive почти без лишней работы)
    cmd.extend(
        [
            "-vf",
            "yadif=0:-1:1,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            str(settings.video_normalize_crf),
            "-an",
            "-movflags",
            "+faststart",
            str(dst),
        ]
    )
    logger.info("ffmpeg: нормализация видео для vision (OpenCV): %s -> %s", src.name, dst.name)
    try:
        subprocess.run(
            cmd,
            check=True,
            timeout=settings.ffmpeg_extract_timeout_sec,
            capture_output=True,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("ffmpeg normalize: превышен таймаут") from e
    except subprocess.CalledProcessError as e:
        tail = ""
        if e.stderr:
            tail = e.stderr.decode(errors="replace")[-1200:]
        raise RuntimeError(f"ffmpeg normalize failed: {tail or e}") from e
