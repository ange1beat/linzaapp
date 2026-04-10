import asyncio
import json
import logging
import shutil
import uuid
from enum import Enum
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from app.config import InferenceBackend, Settings, get_settings
from app.effective_settings import (
    get_effective_settings,
    get_job_defaults_from_storage,
    merge_runtime_config_json,
    public_runtime_view,
)
from app.export_util import build_raw_export, build_time_based_export, parse_audio_results, parse_results_json
from app.linza_taxonomy import LinzaSelection, search_rules, taxonomy_payload
from app.pdf_report import build_job_pdf_bytes
from app.prompt_api import (
    PromptPreviewRequest,
    PromptPreviewResponse,
    _merge_category_lists,
    parse_categories_json,
    parse_linza_json,
    resolve_effective_prompt,
)
from app.prompt_builder import ModerationCategory, build_moderation_prompt
from app.storage import JobStorage, init_db
from app.worker import process_job_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video AI Filter", version="0.1.0")

_storage: JobStorage | None = None
_settings: Settings | None = None
_tasks: set[asyncio.Task[Any]] = set()
_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
_LOGO_SVG = Path(__file__).resolve().parent.parent / "linza-detector-logo.svg"


def _get_storage() -> JobStorage:
    assert _storage is not None
    return _storage


def _get_settings() -> Settings:
    assert _settings is not None
    return _settings


@app.on_event("startup")
def startup() -> None:
    global _storage, _settings
    _settings = get_settings()
    _settings.upload_dir.mkdir(parents=True, exist_ok=True)
    init_db(_settings.db_path)
    _storage = JobStorage(_settings.db_path)
    logger.info(
        "Inference backend=%s (openrouter_model=%s vllm_model=%s)",
        _settings.inference_backend.value,
        _settings.openrouter_model,
        _settings.vllm_model or "(unset)",
    )


def _schedule_job(job_id: str) -> None:
    settings = _get_settings()
    storage = _get_storage()

    async def _run() -> None:
        try:
            await asyncio.to_thread(process_job_sync, job_id, settings, storage)
        except Exception:
            logger.exception("Job %s crashed", job_id)
            storage.set_status(job_id, "failed", error="Internal worker error")

    task = asyncio.create_task(_run())
    _tasks.add(task)

    def _cleanup(t: asyncio.Task[Any]) -> None:
        _tasks.discard(t)

    task.add_done_callback(_cleanup)


class JobCreateResponse(BaseModel):
    job_id: str


class FromPathBody(BaseModel):
    path: str
    prompt: str | None = None
    categories: list[ModerationCategory] | None = None
    linza: LinzaSelection | None = None
    max_frames: int | None = Field(default=None, ge=1)
    max_duration_sec: float | None = Field(default=None, ge=0)


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    error: str | None = None
    frames_total: int | None = None
    frames_done: int = 0
    progress: float | None = None
    processing_phase: str | None = None
    phase_progress: float | None = Field(default=None, ge=0, le=1)
    export_url: str | None = Field(
        default=None,
        description="Когда status=completed: GET {export_url}?format=time-based|raw",
    )


class ExportFormat(str, Enum):
    time_based = "time-based"
    raw = "raw"
    pdf = "pdf"


class MetaInferenceResponse(BaseModel):
    inference_backend: str
    model: str
    audio_transcription: bool
    whisper_model: str | None = None


class RuntimeConfigPatch(BaseModel):
    """Поля, сохраняемые в БД и применяемые к каждому job (поверх .env)."""

    model_config = ConfigDict(extra="forbid")

    inference_backend: str | None = None
    openrouter_model: str | None = None
    openrouter_base_url: str | None = None
    http_referer: str | None = None
    http_title: str | None = None
    vllm_base_url: str | None = None
    vllm_model: str | None = None
    sample_interval_sec: float | None = Field(default=None, gt=0)
    openai_timeout_sec: float | None = Field(default=None, gt=0)
    max_retries: int | None = Field(default=None, ge=1)
    jpeg_quality: int | None = Field(default=None, ge=1, le=100)
    vision_parallel_workers: int | None = Field(default=None, ge=1, le=64)
    audio_transcription_enabled: bool | None = None
    whisper_model_size: str | None = None
    whisper_device: str | None = None
    whisper_compute_type: str | None = None
    max_transcript_chars_for_llm: int | None = Field(default=None, ge=500)
    default_prompt: str | None = None
    default_transcript_moderation_prompt: str | None = None
    default_max_frames: int | None = Field(default=None, ge=1)
    default_max_duration_sec: float | None = Field(default=None, ge=0)


def _progress(row: dict[str, Any]) -> float | None:
    phase = (row.get("processing_phase") or "").strip().lower()
    pp = row.get("phase_progress")
    if phase == "normalize" and pp is not None:
        try:
            v = float(pp)
            if 0.0 <= v <= 1.0:
                return min(100.0, 100.0 * v)
        except (TypeError, ValueError):
            pass
    total = row.get("frames_total")
    done = row.get("frames_done") or 0
    if total is None or total <= 0:
        return None
    return min(100.0, 100.0 * float(done) / float(total))


def _load_completed_job(storage: JobStorage, job_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    row = storage.get_job(job_id)
    if row is None:
        raise HTTPException(404, "Job not found")
    if row["status"] != "completed":
        raise HTTPException(409, f"Job is not completed (status={row['status']})")
    results = parse_results_json(row)
    return row, results


def _json_export_response(data: dict[str, Any], *, attachment: bool, filename: str) -> Response:
    body = json.dumps(data, ensure_ascii=False, indent=2)
    headers: dict[str, str] = {}
    if attachment:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return Response(
        content=body,
        media_type="application/json; charset=utf-8",
        headers=headers,
    )


def _resolve_import_path(settings: Settings, raw: str) -> Path:
    if settings.allowed_import_dir is None:
        raise HTTPException(
            503,
            "Server-side import disabled: set ALLOWED_IMPORT_DIR to enable POST /jobs/from-path",
        )
    try:
        p = Path(raw).expanduser().resolve()
    except OSError as e:
        raise HTTPException(400, f"Invalid path: {e}") from e
    base = settings.allowed_import_dir.expanduser().resolve()
    try:
        p.relative_to(base)
    except ValueError as e:
        raise HTTPException(400, "Path must be under ALLOWED_IMPORT_DIR") from e
    if not p.is_file():
        raise HTTPException(400, "File does not exist or is not a file")
    return p


@app.get("/meta/inference", response_model=MetaInferenceResponse)
def meta_inference() -> MetaInferenceResponse:
    """Активный режим инференса и модель (без ключей и URL целиком)."""
    s = get_effective_settings(_get_settings(), _get_storage())
    model = s.vllm_model.strip() if s.inference_backend.value == "vllm" else s.openrouter_model
    return MetaInferenceResponse(
        inference_backend=s.inference_backend.value,
        model=model or "(not configured)",
        audio_transcription=s.audio_transcription_enabled,
        whisper_model=s.whisper_model_size if s.audio_transcription_enabled else None,
    )


@app.get("/meta/runtime-config")
def meta_runtime_config() -> dict[str, Any]:
    """Эффективный конфиг (БД + .env): то же использует воркер и значения по умолчанию для job."""
    return public_runtime_view(_get_settings(), _get_storage())


@app.patch("/meta/runtime-config")
def meta_runtime_config_patch(body: RuntimeConfigPatch) -> dict[str, Any]:
    storage = _get_storage()
    patch = body.model_dump(exclude_none=True)
    if "inference_backend" in patch:
        try:
            patch["inference_backend"] = InferenceBackend(str(patch["inference_backend"]).strip()).value
        except ValueError as e:
            raise HTTPException(400, f"Invalid inference_backend: {e}") from e
    cur = storage.get_runtime_config_json()
    new = merge_runtime_config_json(cur, patch)
    storage.set_runtime_config_json(new)
    logger.info("Runtime config updated (keys=%s)", list(patch.keys()))
    return public_runtime_view(_get_settings(), storage)


@app.get("/meta/taxonomy")
def meta_taxonomy() -> dict[str, Any]:
    """Классификатор Linza: типы контента, легенда, все правила для поиска в UI."""
    return taxonomy_payload()


@app.get("/meta/taxonomy/search")
def meta_taxonomy_search(
    q: str = Query("", description="Подстрока по id, коду, названию"),
    limit: int = Query(80, ge=1, le=500),
) -> dict[str, Any]:
    return {"rules": search_rules(q, limit=limit)}


@app.delete("/meta/runtime-config")
def meta_runtime_config_reset() -> dict[str, str]:
    """Очистить переопределения в БД; снова действуют только переменные окружения."""
    _get_storage().set_runtime_config_json("{}")
    return {"status": "ok", "detail": "runtime_config cleared"}


@app.get("/")
def serve_ui() -> FileResponse:
    index = _STATIC_DIR / "index.html"
    if not index.is_file():
        raise HTTPException(404, "UI not found (static/index.html)")
    return FileResponse(index)


@app.post("/prompt/preview", response_model=PromptPreviewResponse)
def preview_prompt(body: PromptPreviewRequest) -> PromptPreviewResponse:
    merged = _merge_category_lists(body.categories, body.linza)
    if not merged:
        raise HTTPException(
            400,
            "Добавьте хотя бы одну категорию вручную и/или объект linza (content_type_id + rule_ids).",
        )
    try:
        text = build_moderation_prompt(merged, extra_instructions=body.extra_instructions)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return PromptPreviewResponse(prompt=text)


@app.post("/jobs", response_model=JobCreateResponse)
async def create_job(
    file: UploadFile = File(),
    prompt: str | None = Form(default=None),
    categories_json: str | None = Form(default=None),
    linza_json: str | None = Form(default=None),
    max_frames: int | None = Form(default=None),
    max_duration_sec: float | None = Form(default=None),
) -> JobCreateResponse:
    settings = _get_settings()
    storage = _get_storage()
    eff = get_effective_settings(settings, storage)
    jd = get_job_defaults_from_storage(storage)

    if max_frames is None and jd.get("default_max_frames") is not None:
        max_frames = int(jd["default_max_frames"])
    if max_duration_sec is None and jd.get("default_max_duration_sec") is not None:
        max_duration_sec = float(jd["default_max_duration_sec"])

    if max_frames is not None and max_frames < 1:
        raise HTTPException(400, "max_frames must be >= 1")
    if max_duration_sec is not None and max_duration_sec < 0:
        raise HTTPException(400, "max_duration_sec must be >= 0")

    suffix = Path(file.filename or "video.bin").suffix or ".bin"
    if suffix.lower() not in {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".bin"}:
        suffix = ".mp4"

    job_id = str(uuid.uuid4())
    dest = settings.upload_dir / f"{job_id}{suffix}"

    written = 0
    try:
        with open(dest, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                if settings.max_upload_bytes and written > settings.max_upload_bytes:
                    raise HTTPException(413, "File exceeds MAX_UPLOAD_BYTES")
                out.write(chunk)
    except HTTPException:
        dest.unlink(missing_ok=True)
        raise

    cats = parse_categories_json(categories_json)
    linza_sel = parse_linza_json(linza_json)
    effective_prompt = resolve_effective_prompt(eff, prompt, cats, linza_sel)
    merged = _merge_category_lists(cats, linza_sel)
    cats_stored: str | None = None
    if merged:
        cats_stored = json.dumps([c.model_dump() for c in merged], ensure_ascii=False)
    elif categories_json and str(categories_json).strip():
        cats_stored = categories_json.strip()
    linza_stored = linza_sel.model_dump_json() if linza_sel else None
    storage.create_job(
        str(dest.resolve()),
        effective_prompt,
        frames_total=None,
        max_frames=max_frames,
        max_duration_sec=max_duration_sec,
        job_id=job_id,
        categories_json=cats_stored,
        linza_selection_json=linza_stored,
    )
    _schedule_job(job_id)
    return JobCreateResponse(job_id=job_id)


@app.post("/jobs/from-path", response_model=JobCreateResponse)
async def create_job_from_path(body: FromPathBody) -> JobCreateResponse:
    settings = _get_settings()
    storage = _get_storage()
    eff = get_effective_settings(settings, storage)
    jd = get_job_defaults_from_storage(storage)
    src = _resolve_import_path(settings, body.path)
    job_id = str(uuid.uuid4())
    suffix = src.suffix or ".mp4"
    dest = settings.upload_dir / f"{job_id}{suffix}"

    try:
        dest.hardlink_to(src)
    except OSError:
        try:
            await asyncio.to_thread(shutil.copy2, src, dest)
        except OSError as e:
            raise HTTPException(500, f"Could not link or copy file: {e}") from e

    max_frames = body.max_frames
    max_duration_sec = body.max_duration_sec
    if max_frames is None and jd.get("default_max_frames") is not None:
        max_frames = int(jd["default_max_frames"])
    if max_duration_sec is None and jd.get("default_max_duration_sec") is not None:
        max_duration_sec = float(jd["default_max_duration_sec"])

    effective_prompt = resolve_effective_prompt(eff, body.prompt, body.categories, body.linza)
    merged = _merge_category_lists(body.categories, body.linza)
    cats_stored = (
        json.dumps([c.model_dump() for c in merged], ensure_ascii=False) if merged else None
    )
    if not cats_stored and body.categories:
        cats_stored = json.dumps([c.model_dump() for c in body.categories], ensure_ascii=False)
    linza_stored = body.linza.model_dump_json() if body.linza else None
    storage.create_job(
        str(dest.resolve()),
        effective_prompt,
        frames_total=None,
        max_frames=max_frames,
        max_duration_sec=max_duration_sec,
        job_id=job_id,
        categories_json=cats_stored,
        linza_selection_json=linza_stored,
    )
    _schedule_job(job_id)
    return JobCreateResponse(job_id=job_id)


@app.get(
    "/jobs/{job_id}/export",
    summary="Скачать результат в JSON",
    description=(
        "Удобная выгрузка: `format=time-based` — отчёт TIME_BASED_REPORT (как внешний пайплайн); "
        "`format=raw` — сырые вердикты по каждому сэмплу. "
        "`attachment=false` — без заголовка скачивания (удобно для `curl | jq`)."
    ),
)
def export_job_json(
    job_id: str,
    export_format: ExportFormat = Query(
        default=ExportFormat.time_based,
        alias="format",
        description="time-based | raw | pdf",
    ),
    attachment: bool = Query(
        default=True,
        description="false = inline JSON без Content-Disposition",
    ),
) -> Response:
    storage = _get_storage()
    row, results = _load_completed_job(storage, job_id)
    if export_format is ExportFormat.pdf:
        pdf_bytes = build_job_pdf_bytes(
            job_id=job_id,
            row=row,
            results=results,
            logo_path=_LOGO_SVG if _LOGO_SVG.is_file() else None,
        )
        headers: dict[str, str] = {}
        if attachment:
            headers["Content-Disposition"] = f'attachment; filename="job_{job_id}_report.pdf"'
        return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
    if export_format is ExportFormat.raw:
        payload = build_raw_export(job_id, results, row=row)
        fname = f"job_{job_id}_raw.json"
    else:
        payload = build_time_based_export(row, results, job_id=job_id)
        fname = f"job_{job_id}_time_based.json"
    return _json_export_response(payload, attachment=attachment, filename=fname)


@app.get("/jobs/{job_id}/results")
def get_results(job_id: str) -> dict[str, Any]:
    storage = _get_storage()
    row, results = _load_completed_job(storage, job_id)
    out: dict[str, Any] = {"job_id": job_id, "results": results}
    audio = parse_audio_results(row)
    if audio is not None:
        out["audio"] = audio
    return out


@app.get("/jobs/{job_id}/report.json")
def download_time_report_legacy(job_id: str) -> Response:
    """Совместимость: то же, что GET /jobs/{id}/export?format=time-based."""
    storage = _get_storage()
    row, results = _load_completed_job(storage, job_id)
    payload = build_time_based_export(row, results, job_id=job_id)
    return _json_export_response(
        payload,
        attachment=True,
        filename=f"job_{job_id}_time_based.json",
    )


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str) -> JobStatusResponse:
    storage = _get_storage()
    row = storage.get_job(job_id)
    if row is None:
        raise HTTPException(404, "Job not found")
    return JobStatusResponse(
        job_id=job_id,
        status=row["status"],
        error=row.get("error"),
        frames_total=row.get("frames_total"),
        frames_done=int(row.get("frames_done") or 0),
        progress=_progress(row),
        processing_phase=row.get("processing_phase"),
        phase_progress=row.get("phase_progress"),
        export_url=f"/jobs/{job_id}/export" if row["status"] == "completed" else None,
    )


@app.delete("/jobs/{job_id}")
def delete_job(job_id: str) -> dict[str, str]:
    storage = _get_storage()
    row = storage.get_job(job_id)
    if row is None:
        raise HTTPException(404, "Job not found")

    storage.set_cancelled(job_id)
    st = row["status"]

    if st in ("completed", "failed"):
        vp = row.get("video_path")
        if vp:
            try:
                Path(vp).unlink(missing_ok=True)
            except OSError as e:
                logger.warning("Unlink %s: %s", vp, e)
        storage.delete_job_record(job_id)
        return {"job_id": job_id, "status": "deleted"}

    # Активная джоба: не трогаем файл — воркер сам снимет после выхода по cancelled
    return {"job_id": job_id, "status": "cancelling"}
