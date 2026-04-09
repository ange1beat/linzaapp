"""Прогрессивный H.264 для OpenCV: interlaced yuv420p ломает swscale при выводе в BGR."""

from __future__ import annotations

import json
import logging
import subprocess
import threading
import time
from collections.abc import Callable
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


def probe_duration_sec(src: Path, ffprobe_bin: str) -> float | None:
    cmd = [
        ffprobe_bin,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
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
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    raw = (proc.stdout or "").strip()
    if not raw or raw == "N/A":
        return None
    try:
        d = float(raw)
    except ValueError:
        return None
    return d if d > 0 else None


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
    *,
    on_progress: Callable[[float], None] | None = None,
) -> None:
    """Деинтерлейс (только помеченные interlaced кадры) → progressive yuv420p, без аудио.

    on_progress(0..1) вызывается по мере кодирования (по out_time_us и длительности из ffprobe).
    """
    dst.parent.mkdir(parents=True, exist_ok=True)

    duration_sec = probe_duration_sec(src, settings.ffprobe_path)
    if duration_limit_sec is not None and duration_limit_sec > 0:
        if duration_sec is not None:
            duration_sec = min(duration_sec, duration_limit_sec)
        else:
            duration_sec = duration_limit_sec

    cmd: list[str] = [
        settings.ffmpeg_path,
        "-y",
        "-hide_banner",
        "-nostats",
        "-loglevel",
        "error",
        "-progress",
        "pipe:1",
        "-i",
        str(src),
    ]
    if duration_limit_sec is not None and duration_limit_sec > 0:
        cmd.extend(["-t", f"{duration_limit_sec:.3f}"])
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

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    stderr_buf: list[str] = []

    def _drain_stderr() -> None:
        if proc.stderr:
            for line in iter(proc.stderr.readline, ""):
                stderr_buf.append(line)

    t_err = threading.Thread(target=_drain_stderr, daemon=True)
    t_err.start()

    last_emit = 0.0
    last_p = -1.0
    try:
        if proc.stdout is None:
            raise RuntimeError("ffmpeg: stdout not available")
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k == "out_time_us" and on_progress and duration_sec and duration_sec > 0:
                try:
                    us = int(v)
                except ValueError:
                    continue
                p = min(1.0, max(0.0, us / (duration_sec * 1_000_000.0)))
                now = time.time()
                if p - last_p >= 0.02 or now - last_emit >= 0.35:
                    last_emit = now
                    last_p = p
                    on_progress(p)
            elif k == "progress" and v == "end":
                break

        try:
            rc = proc.wait(timeout=settings.ffmpeg_extract_timeout_sec)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                pass
            raise RuntimeError("ffmpeg normalize: превышен таймаут") from None
        if rc != 0:
            tail = "".join(stderr_buf)[-1200:]
            raise RuntimeError(f"ffmpeg normalize failed (rc={rc}): {tail or 'no stderr'}")
        if on_progress:
            on_progress(1.0)
    finally:
        t_err.join(timeout=5.0)
