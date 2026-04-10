from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.linza_taxonomy import (
    build_default_server_prompt_with_full_linza,
    build_default_transcript_moderation_prompt_with_full_linza,
)


class InferenceBackend(str, Enum):
    """openrouter: OpenRouter; vllm: локальный OpenAI-compatible сервер (vLLM)."""

    openrouter = "openrouter"
    vllm = "vllm"


def _empty_to_none(v: str | Path | None) -> Path | None:
    if v is None or v == "":
        return None
    return Path(v) if not isinstance(v, Path) else v


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    inference_backend: InferenceBackend = InferenceBackend.openrouter

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "qwen/qwen3-vl-8b-thinking"
    http_referer: str = "https://github.com/video-ai-filter"
    http_title: str = "Video AI Filter"

    vllm_base_url: str = "http://127.0.0.1:8001/v1"
    vllm_api_key: str = "EMPTY"
    vllm_model: str = ""

    upload_dir: Path = Path("./data/uploads")
    db_path: Path = Path("./data/jobs.db")
    allowed_import_dir: Annotated[Path | None, BeforeValidator(_empty_to_none)] = None

    default_prompt: str = Field(default_factory=build_default_server_prompt_with_full_linza)

    max_upload_bytes: int = 0
    sample_interval_sec: float = 0.5
    openai_timeout_sec: float = 300.0
    max_retries: int = 5
    jpeg_quality: int = 85
    vision_parallel_workers: int = Field(default=30, ge=1, le=64)

    audio_transcription_enabled: bool = True
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    ffmpeg_extract_timeout_sec: int = 7200
    # auto: ffprobe field_order tt/tb/bt/bb → перекод перед OpenCV; always/never — принудительно
    video_ffmpeg_normalize: Literal["auto", "always", "never"] = "auto"
    video_normalize_crf: int = Field(default=23, ge=18, le=35)
    whisper_model_size: str = "tiny"
    whisper_device: str = "auto"
    whisper_compute_type: str = "auto"
    max_transcript_chars_for_llm: int = 24000

    default_transcript_moderation_prompt: str = Field(
        default_factory=build_default_transcript_moderation_prompt_with_full_linza
    )


def get_settings() -> Settings:
    return Settings()
