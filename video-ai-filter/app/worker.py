import base64
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any

import cv2
from openai import APIError, OpenAI, RateLimitError

from app.audio_moderation import run_audio_moderation_pipeline
from app.config import Settings
from app.effective_settings import get_effective_settings
from app.inference import ResolvedInference, resolve_inference, validate_inference_settings
from app.storage import JobStorage

logger = logging.getLogger(__name__)


def _preview_for_log(text: str, max_len: int = 180) -> str:
    s = (text or "").replace("\n", " ").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def _estimate_frame_count(
    duration_sec: float,
    fps: float,
    interval: float,
    max_duration_sec: float | None,
    max_frames: int | None,
) -> int:
    effective_duration = duration_sec
    if max_duration_sec is not None:
        effective_duration = min(effective_duration, max_duration_sec)
    if effective_duration <= 0 or fps <= 0:
        return 0
    n = int(effective_duration / interval) + 1
    if max_frames is not None:
        n = min(n, max_frames)
    return max(n, 0)


def _video_duration_and_fps(cap: cv2.VideoCapture) -> tuple[float, float]:
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
    if fps > 0 and frame_count > 0:
        duration = frame_count / fps
        return duration, fps
    return 0.0, fps if fps > 0 else 25.0


def _encode_jpeg_b64(frame: Any, quality: int) -> str:
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise RuntimeError("cv2.imencode failed")
    return base64.standard_b64encode(buf.tobytes()).decode("ascii")


def _call_vision_chat(
    client: OpenAI,
    model: str,
    prompt: str,
    image_b64: str,
    settings: Settings,
) -> str:
    last_err: Exception | None = None
    for attempt in range(settings.max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}",
                                },
                            },
                        ],
                    }
                ],
            )
            choice = resp.choices[0]
            content = choice.message.content
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
        logger.warning("Vision LLM request failed (attempt %s): %s; retry in %ss", attempt + 1, last_err, wait)
        time.sleep(wait)
    assert last_err is not None
    raise last_err


def _sample_entry_from_verdict(verdict_raw: str, t: float, frame_idx: int) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "time_sec": round(t, 3),
        "frame_index": frame_idx,
        "verdict_raw": verdict_raw,
    }
    try:
        parsed = json.loads(verdict_raw)
        if isinstance(parsed, dict):
            entry["verdict_parsed"] = parsed
    except json.JSONDecodeError:
        pass
    return entry


def _vision_one_sample(
    client: OpenAI,
    model: str,
    prompt: str,
    settings: Settings,
    job_id: str,
    t: float,
    frame_idx: int,
    image_b64: str,
) -> tuple[int, dict[str, Any]]:
    verdict_raw = _call_vision_chat(client, model, prompt, image_b64, settings)
    logger.info(
        "Job %s vision LLM t=%.3fs frame_idx=%d chars=%d preview=%s",
        job_id,
        t,
        frame_idx,
        len(verdict_raw),
        _preview_for_log(verdict_raw),
    )
    return frame_idx, _sample_entry_from_verdict(verdict_raw, t, frame_idx)


def process_job_sync(job_id: str, base_settings: Settings, storage: JobStorage) -> None:
    settings = get_effective_settings(base_settings, storage)
    cfg_err = validate_inference_settings(settings)
    if cfg_err:
        storage.set_status(job_id, "failed", error=cfg_err)
        row = storage.get_job(job_id)
        if row:
            Path(row["video_path"]).unlink(missing_ok=True)
        return

    row = storage.get_job(job_id)
    if not row:
        return

    if storage.is_cancelled(job_id):
        storage.set_status(job_id, "failed", error="Cancelled before start")
        Path(row["video_path"]).unlink(missing_ok=True)
        return

    video_path = Path(row["video_path"])
    prompt = row["prompt"]
    max_frames = row["max_frames"]
    max_duration_sec = row["max_duration_sec"]

    if not video_path.is_file():
        storage.set_status(job_id, "failed", error=f"Video file missing: {video_path}")
        return

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        storage.set_status(job_id, "failed", error="Could not open video with OpenCV")
        video_path.unlink(missing_ok=True)
        return

    try:
        duration_sec, fps = _video_duration_and_fps(cap)
        fc_raw = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
        fc_int = int(fc_raw) if fc_raw > 0 else None
        fps_meta = float(fps) if fps and fps > 0 else None
        storage.set_video_metadata(job_id, video_fps=fps_meta, video_frame_count=fc_int)

        interval = settings.sample_interval_sec
        estimated = _estimate_frame_count(duration_sec, fps, interval, max_duration_sec, max_frames)
        storage.set_status(job_id, "processing", frames_total=estimated, frames_done=0)

        inf: ResolvedInference = resolve_inference(settings)
        logger.info(
            "Job %s inference backend=%s model=%s base=%s",
            job_id,
            inf.backend.value,
            inf.model,
            inf.client.base_url,
        )
        logger.info(
            "Job %s vision: sampled frames every %.3fs (LLM sees keyframes only). Audio/ASR runs once after all frames.",
            job_id,
            interval,
        )

        samples: list[tuple[float, int, str]] = []
        next_sample_t = 0.0
        frame_idx = 0
        sampled = 0

        while True:
            if storage.is_cancelled(job_id):
                storage.set_status(job_id, "failed", error="Cancelled")
                return

            ret, frame = cap.read()
            if not ret:
                break

            t = frame_idx / fps if fps > 0 else 0.0
            if max_duration_sec is not None and t > max_duration_sec + 1e-6:
                break

            if t + 1e-6 >= next_sample_t:
                if max_frames is not None and sampled >= max_frames:
                    break
                try:
                    b64 = _encode_jpeg_b64(frame, settings.jpeg_quality)
                except Exception as e:
                    logger.exception("JPEG encode at t=%s failed", t)
                    storage.set_status(job_id, "failed", error=str(e), frames_done=0)
                    video_path.unlink(missing_ok=True)
                    return
                samples.append((t, frame_idx, b64))
                sampled += 1
                next_sample_t += interval

            frame_idx += 1

        workers = max(1, settings.vision_parallel_workers)
        logger.info(
            "Job %s vision: %d sampled frames, calling LLM with up to %d parallel workers",
            job_id,
            len(samples),
            workers,
        )

        results_by_frame: dict[int, dict[str, Any]] = {}
        results_lock = Lock()
        processed = 0
        abort = False

        executor = ThreadPoolExecutor(max_workers=workers)
        try:
            futures = [
                executor.submit(
                    _vision_one_sample,
                    inf.client,
                    inf.model,
                    prompt,
                    settings,
                    job_id,
                    t,
                    fi,
                    b64,
                )
                for t, fi, b64 in samples
            ]
            for fut in as_completed(futures):
                if storage.is_cancelled(job_id):
                    storage.set_status(job_id, "failed", error="Cancelled", frames_done=processed)
                    video_path.unlink(missing_ok=True)
                    abort = True
                    break
                try:
                    idx, entry = fut.result()
                except Exception as e:
                    logger.exception("Vision LLM sample failed")
                    storage.set_status(job_id, "failed", error=str(e), frames_done=processed)
                    video_path.unlink(missing_ok=True)
                    abort = True
                    break
                with results_lock:
                    results_by_frame[idx] = entry
                    ordered = [results_by_frame[i] for i in sorted(results_by_frame)]
                    processed = len(ordered)
                    storage.append_result(job_id, ordered)
                    storage.increment_frames_done(job_id, processed)
        finally:
            executor.shutdown(wait=not abort, cancel_futures=abort)

        if abort:
            return

        processed = len(samples)
        logger.info("Job %s vision phase done: %d sampled frames", job_id, processed)

        if settings.audio_transcription_enabled:
            row_audio = storage.get_job(job_id)
            if row_audio:
                try:
                    audio_payload = run_audio_moderation_pipeline(
                        video_path,
                        row_audio,
                        inf,
                        settings,
                    )
                    storage.set_audio_results(job_id, json.dumps(audio_payload, ensure_ascii=False))
                except Exception as e:
                    logger.exception("Audio / Whisper pipeline")
                    storage.set_audio_results(
                        job_id,
                        json.dumps({"error": "audio_pipeline", "detail": str(e)}, ensure_ascii=False),
                    )

        storage.set_status(job_id, "completed", frames_done=processed, frames_total=max(estimated, processed))
    finally:
        cap.release()

    try:
        video_path.unlink(missing_ok=True)
    except OSError as e:
        logger.warning("Could not remove upload %s: %s", video_path, e)
