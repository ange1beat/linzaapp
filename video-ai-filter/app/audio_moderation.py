"""Transcribe video audio and run text moderation via the same LLM client."""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

from openai import APIError, OpenAI, RateLimitError

from app.audio_whisper import extract_audio_wav, transcribe_wav, truncate_transcript
from app.config import Settings
from app.inference import ResolvedInference
from app.job_categories import categories_from_job_row
from app.prompt_builder import build_transcript_moderation_prompt

logger = logging.getLogger(__name__)


def _preview_for_log(text: str, max_len: int = 220) -> str:
    s = (text or "").replace("\n", " ").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def _call_text_chat(
    client: OpenAI,
    model: str,
    user_message: str,
    settings: Settings,
) -> str:
    last_err: Exception | None = None
    for attempt in range(settings.max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": user_message}],
            )
            content = resp.choices[0].message.content
            return (content or "").strip()
        except RateLimitError as e:
            last_err = e
        except APIError as e:
            last_err = e
            code = getattr(e, "status_code", None)
            if code is not None and code not in (429, 500, 502, 503, 504):
                raise
        except Exception as e:
            last_err = e
        wait = min(2**attempt, 60)
        logger.warning("Text LLM request failed (attempt %s): %s; retry in %ss", attempt + 1, last_err, wait)
        time.sleep(wait)
    assert last_err is not None
    raise last_err


def run_audio_moderation_pipeline(
    video_path: Path,
    row: dict[str, Any],
    inf: ResolvedInference,
    settings: Settings,
) -> dict[str, Any]:
    job_id = row.get("id", "job")
    wav_path = video_path.parent / f"{job_id}_extract.wav"
    max_dur = row.get("max_duration_sec")
    duration_limit: float | None = float(max_dur) if max_dur is not None else None

    logger.info(
        "Job %s audio: single full-file extract → Whisper (not per frame). ffmpeg limit_sec=%s",
        job_id,
        duration_limit if duration_limit and duration_limit > 0 else "full",
    )

    try:
        extract_audio_wav(video_path, wav_path, settings, duration_limit_sec=duration_limit)
        if wav_path.is_file():
            logger.info("Job %s ffmpeg: wav_bytes=%s", job_id, wav_path.stat().st_size)
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode("utf-8", errors="replace")[:4000]
        return {"error": "ffmpeg_extract_failed", "detail": err or str(e)}
    except subprocess.TimeoutExpired:
        return {"error": "ffmpeg_timeout", "detail": "Audio extract exceeded ffmpeg_extract_timeout_sec"}
    except FileNotFoundError:
        return {
            "error": "ffmpeg_not_found",
            "detail": f"Executable not found: {settings.ffmpeg_path}",
        }
    except Exception as e:
        logger.exception("ffmpeg extract")
        return {"error": "ffmpeg_extract_failed", "detail": str(e)}

    try:
        asr = transcribe_wav(wav_path, settings)
    except Exception as e:
        logger.exception("Whisper transcribe")
        return {"error": "whisper_failed", "detail": str(e)}
    finally:
        try:
            wav_path.unlink(missing_ok=True)
        except OSError:
            pass

    if not (asr.get("text") or "").strip():
        return {
            "transcript": "",
            "segments": asr.get("segments") or [],
            "language": asr.get("language"),
            "duration": asr.get("duration"),
            "moderation_raw": None,
            "moderation_note": "no_speech_detected",
        }

    cats = categories_from_job_row(row)
    if cats:
        try:
            instr = build_transcript_moderation_prompt(cats)
        except ValueError:
            instr = settings.default_transcript_moderation_prompt
    else:
        instr = settings.default_transcript_moderation_prompt

    truncated = truncate_transcript(asr["text"], settings.max_transcript_chars_for_llm)
    body_parts = [instr, "", "### Transcript", truncated]
    segs = asr.get("segments") or []
    if segs and len(segs) <= 400:
        body_parts.extend(["", "### Segments (seconds)", ""])
        body_parts.extend(f"[{s['start']} – {s['end']}] {s['text']}" for s in segs)
    user_message = "\n".join(body_parts)

    try:
        mod_raw = _call_text_chat(inf.client, inf.model, user_message, settings)
    except Exception as e:
        logger.exception("Transcript moderation LLM")
        return {
            "transcript": asr["text"],
            "segments": segs,
            "language": asr.get("language"),
            "duration": asr.get("duration"),
            "moderation_error": str(e),
        }

    logger.info(
        "Job %s transcript moderation LLM: chars_out=%s preview=%s",
        job_id,
        len(mod_raw),
        _preview_for_log(mod_raw),
    )

    out: dict[str, Any] = {
        "transcript": asr["text"],
        "segments": segs,
        "language": asr.get("language"),
        "duration": asr.get("duration"),
        "moderation_raw": mod_raw,
    }
    try:
        parsed = json.loads(mod_raw)
        if isinstance(parsed, dict):
            out["moderation_parsed"] = parsed
    except json.JSONDecodeError:
        pass
    return out
