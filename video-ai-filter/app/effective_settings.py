"""Слияние переменных окружения (.env) с конфигом из БД (настройки из UI)."""

from __future__ import annotations

import json
from typing import Any

from app.config import InferenceBackend, Settings
from app.storage import JobStorage

# Поля Settings, которые можно переопределить из UI/БД (без секретов и путей).
RUNTIME_OVERRIDABLE: frozenset[str] = frozenset(
    {
        "inference_backend",
        "openrouter_model",
        "openrouter_base_url",
        "http_referer",
        "http_title",
        "vllm_base_url",
        "vllm_model",
        "sample_interval_sec",
        "openai_timeout_sec",
        "max_retries",
        "jpeg_quality",
        "vision_parallel_workers",
        "audio_transcription_enabled",
        "whisper_model_size",
        "whisper_device",
        "whisper_compute_type",
        "max_transcript_chars_for_llm",
        "default_prompt",
        "default_transcript_moderation_prompt",
    }
)

JOB_DEFAULT_KEYS: frozenset[str] = frozenset({"default_max_frames", "default_max_duration_sec"})


def _coerce_value(key: str, value: Any) -> Any:
    if key == "inference_backend" and isinstance(value, str):
        return InferenceBackend(value.strip())
    return value


def get_runtime_overrides_dict(storage: JobStorage) -> dict[str, Any]:
    raw = storage.get_runtime_config_json()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def get_job_defaults_from_storage(storage: JobStorage) -> dict[str, Any]:
    data = get_runtime_overrides_dict(storage)
    out: dict[str, Any] = {}
    for k in JOB_DEFAULT_KEYS:
        if k in data and data[k] is not None:
            out[k] = data[k]
    return out


def get_effective_settings(base: Settings, storage: JobStorage) -> Settings:
    data = get_runtime_overrides_dict(storage)
    patch: dict[str, Any] = {}
    for k, v in data.items():
        if k in RUNTIME_OVERRIDABLE and v is not None:
            patch[k] = _coerce_value(k, v)
    if not patch:
        return base
    return base.model_copy(update=patch)


def merge_runtime_config_json(current_json: str | None, patch: dict[str, Any]) -> str:
    cur: dict[str, Any] = {}
    if current_json:
        try:
            loaded = json.loads(current_json)
            if isinstance(loaded, dict):
                cur = loaded
        except json.JSONDecodeError:
            pass
    for k, v in patch.items():
        if v is None:
            cur.pop(k, None)
        else:
            cur[k] = v
    return json.dumps(cur, ensure_ascii=False)


def public_runtime_view(base: Settings, storage: JobStorage) -> dict[str, Any]:
    """Эффективные значения для UI и GET /meta/runtime-config (без ключей API)."""
    eff = get_effective_settings(base, storage)
    jd = get_job_defaults_from_storage(storage)
    return {
        "inference_backend": eff.inference_backend.value,
        "openrouter_model": eff.openrouter_model,
        "openrouter_base_url": eff.openrouter_base_url,
        "http_referer": eff.http_referer,
        "http_title": eff.http_title,
        "vllm_base_url": eff.vllm_base_url,
        "vllm_model": eff.vllm_model,
        "sample_interval_sec": eff.sample_interval_sec,
        "openai_timeout_sec": eff.openai_timeout_sec,
        "max_retries": eff.max_retries,
        "jpeg_quality": eff.jpeg_quality,
        "vision_parallel_workers": eff.vision_parallel_workers,
        "audio_transcription_enabled": eff.audio_transcription_enabled,
        "whisper_model_size": eff.whisper_model_size,
        "whisper_device": eff.whisper_device,
        "whisper_compute_type": eff.whisper_compute_type,
        "max_transcript_chars_for_llm": eff.max_transcript_chars_for_llm,
        "default_prompt": eff.default_prompt,
        "default_transcript_moderation_prompt": eff.default_transcript_moderation_prompt,
        "default_max_frames": jd.get("default_max_frames"),
        "default_max_duration_sec": jd.get("default_max_duration_sec"),
    }
