"""Extract audio with ffmpeg; transcribe with faster-whisper (lightweight models)."""

from __future__ import annotations

import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from app.config import Settings

logger = logging.getLogger(__name__)

_whisper_lock = threading.Lock()
_whisper_model = None
_whisper_cache_key: tuple[str, str, str] | None = None


def _resolve_whisper_device(settings: Settings) -> str:
    d = (settings.whisper_device or "auto").strip().lower()
    if d == "auto":
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"
    return d


def _resolve_whisper_compute_type(settings: Settings, device: str) -> str:
    ct = (settings.whisper_compute_type or "auto").strip().lower()
    if ct and ct != "auto":
        return ct
    return "int8" if device == "cpu" else "float16"


def _get_whisper_model(settings: Settings) -> Any:
    global _whisper_model, _whisper_cache_key
    device = _resolve_whisper_device(settings)
    compute_type = _resolve_whisper_compute_type(settings, device)
    key = (settings.whisper_model_size, device, compute_type)
    with _whisper_lock:
        if _whisper_model is not None and _whisper_cache_key == key:
            return _whisper_model
        from faster_whisper import WhisperModel

        logger.info(
            "Loading Whisper model=%s device=%s compute_type=%s",
            settings.whisper_model_size,
            device,
            compute_type,
        )
        _whisper_model = WhisperModel(
            settings.whisper_model_size,
            device=device,
            compute_type=compute_type,
        )
        _whisper_cache_key = key
        return _whisper_model


def extract_audio_wav(
    video_path: Path,
    wav_path: Path,
    settings: Settings,
    *,
    duration_limit_sec: float | None = None,
) -> None:
    """Extract mono 16 kHz WAV. If duration_limit_sec is set, only first N seconds (aligns with vision cap)."""
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        settings.ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(video_path),
    ]
    if duration_limit_sec is not None and duration_limit_sec > 0:
        cmd.extend(["-t", str(duration_limit_sec)])
    cmd.extend(
        [
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(wav_path),
        ]
    )
    subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        timeout=settings.ffmpeg_extract_timeout_sec,
    )


def transcribe_wav(wav_path: Path, settings: Settings) -> dict[str, Any]:
    wav_size = wav_path.stat().st_size if wav_path.is_file() else 0
    t0 = time.perf_counter()
    model = _get_whisper_model(settings)
    segments_iter, info = model.transcribe(
        str(wav_path),
        beam_size=1,
        vad_filter=True,
        word_timestamps=False,
    )
    segments: list[dict[str, Any]] = []
    texts: list[str] = []
    for seg in segments_iter:
        seg_start = round(float(seg.start), 3)
        seg_end = round(float(seg.end), 3)
        tx = (seg.text or "").strip()
        if tx:
            texts.append(tx)
            segments.append({"start": seg_start, "end": seg_end, "text": tx})
    full_text = " ".join(texts).strip()
    elapsed = time.perf_counter() - t0
    lang = getattr(info, "language", None)
    dur = round(float(info.duration), 3) if getattr(info, "duration", None) else None
    logger.info(
        "Whisper: wav_bytes=%s model=%s audio_duration_sec=%s segments=%d transcript_chars=%d lang=%s wall_sec=%.2f",
        wav_size,
        settings.whisper_model_size,
        dur,
        len(segments),
        len(full_text),
        lang,
        elapsed,
    )
    if full_text:
        prev = full_text.replace("\n", " ").strip()
        if len(prev) > 240:
            prev = prev[:237] + "..."
        logger.info("Whisper transcript preview: %s", prev)
    else:
        logger.info("Whisper: empty transcript (no speech or silence)")
    return {
        "text": full_text,
        "segments": segments,
        "language": lang,
        "duration": dur,
    }


def truncate_transcript(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    half = max_chars // 2 - 80
    if half < 100:
        return text[:max_chars]
    return text[:half] + "\n\n[... transcript truncated ...]\n\n" + text[-half:]
