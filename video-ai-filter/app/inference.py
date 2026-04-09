"""Two inference modes: OpenRouter (cloud) or vLLM (local OpenAI-compatible server)."""

from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from app.config import InferenceBackend, Settings


@dataclass(frozen=True)
class ResolvedInference:
    client: OpenAI
    model: str
    backend: InferenceBackend


def validate_inference_settings(settings: Settings) -> str | None:
    """Return error message if configuration is invalid for the selected backend."""
    b = settings.inference_backend
    if b == InferenceBackend.openrouter:
        if not (settings.openrouter_api_key or "").strip():
            return "OPENROUTER_API_KEY is not set (INFERENCE_BACKEND=openrouter)"
        return None
    if b == InferenceBackend.vllm:
        if not (settings.vllm_base_url or "").strip():
            return "VLLM_BASE_URL is not set (INFERENCE_BACKEND=vllm)"
        if not (settings.vllm_model or "").strip():
            return "VLLM_MODEL is not set (INFERENCE_BACKEND=vllm)"
        return None
    return f"Unknown INFERENCE_BACKEND: {b!r}"


def resolve_inference(settings: Settings) -> ResolvedInference:
    """Build OpenAI SDK client for the active backend (same chat + vision message shape)."""
    timeout = settings.openai_timeout_sec
    b = settings.inference_backend

    if b == InferenceBackend.openrouter:
        client = OpenAI(
            api_key=settings.openrouter_api_key.strip(),
            base_url=settings.openrouter_base_url.rstrip("/"),
            timeout=timeout,
            default_headers={
                "HTTP-Referer": settings.http_referer,
                "X-Title": settings.http_title,
            },
        )
        return ResolvedInference(
            client=client,
            model=settings.openrouter_model,
            backend=b,
        )

    client = OpenAI(
        api_key=(settings.vllm_api_key or "EMPTY").strip() or "EMPTY",
        base_url=settings.vllm_base_url.rstrip("/"),
        timeout=timeout,
        default_headers={},
    )
    return ResolvedInference(
        client=client,
        model=settings.vllm_model.strip(),
        backend=b,
    )
