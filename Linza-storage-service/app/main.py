import contextvars
import os
import logging
import tempfile
from contextlib import asynccontextmanager

from pythonjsonlogger.json import JsonFormatter as JsonLogFormatter

_request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


class RequestIDFilter(logging.Filter):
    """Inject request_id from ContextVar into every log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx.get()
        return True
import traceback
import uuid

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.routes import files, config
from app.tasks import init_task_store, shutdown_task_store

def configure_logging(service_name: str) -> None:
    handler = logging.StreamHandler()
    formatter = JsonLogFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
        static_fields={"service": service_name},
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())
    logging.root.handlers.clear()
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)


configure_logging("storage-service")
logger = logging.getLogger("storage-service")

ERROR_TRACKER_URL = os.getenv("ERROR_TRACKER_URL", "http://localhost:8004")
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "")


class ServiceKeyMiddleware(BaseHTTPMiddleware):
    """Validate X-Service-Key header for inter-service auth."""
    async def dispatch(self, request: Request, call_next) -> Response:
        if not SERVICE_API_KEY:
            return await call_next(request)
        if request.url.path == "/health":
            return await call_next(request)
        key = request.headers.get("x-service-key", "")
        if key != SERVICE_API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing service key"})
        return await call_next(request)


class ErrorReporterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())[:8]
        _request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error("[%s] Unhandled exception: %s", request_id, exc, exc_info=True)
            try:
                _h = {"X-Service-Key": SERVICE_API_KEY} if SERVICE_API_KEY else {}
                async with httpx.AsyncClient(timeout=5) as client:
                    await client.post(f"{ERROR_TRACKER_URL}/api/errors/report", headers=_h, json={
                        "service": "storage-service",
                        "severity": "critical",
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                        "endpoint": str(request.url.path),
                        "method": request.method,
                        "status_code": 500,
                        "request_id": request_id,
                    })
            except Exception:
                pass
            resp = JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
            resp.headers["X-Request-ID"] = request_id
            return resp
        if response.status_code >= 500:
            try:
                _h = {"X-Service-Key": SERVICE_API_KEY} if SERVICE_API_KEY else {}
                async with httpx.AsyncClient(timeout=5) as client:
                    await client.post(f"{ERROR_TRACKER_URL}/api/errors/report", headers=_h, json={
                        "service": "storage-service",
                        "severity": "error",
                        "message": f"HTTP {response.status_code} on {request.method} {request.url.path}",
                        "endpoint": str(request.url.path),
                        "method": request.method,
                        "status_code": response.status_code,
                        "request_id": request_id,
                    })
            except Exception:
                pass
        response.headers["X-Request-ID"] = request_id
        return response


TEMP_DIR = os.path.join(tempfile.gettempdir(), "linza-storage")


def _cleanup_temp_dir() -> None:
    """Remove orphaned temp files left by a previous crash."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    removed = 0
    for name in os.listdir(TEMP_DIR):
        path = os.path.join(TEMP_DIR, name)
        try:
            if os.path.isfile(path):
                os.unlink(path)
                removed += 1
            else:
                logger.warning("Unexpected directory in temp dir: %s", path)
        except OSError as exc:
            logger.warning("Failed to remove orphaned temp file %s: %s", path, exc)
    if removed:
        logger.info("Cleaned %d orphaned temp file(s) from %s", removed, TEMP_DIR)


@asynccontextmanager
async def lifespan(app):
    _cleanup_temp_dir()
    init_task_store()

    # Reconfigure uvicorn loggers → JSON via root handler (board#38)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True

    yield
    shutdown_task_store()


app = FastAPI(
    title="Linza Storage Service",
    description="Сервис хранения файлов и управления доступом к ним",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(ErrorReporterMiddleware)
app.add_middleware(ServiceKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router, prefix="/api/files")
app.include_router(config.router, prefix="/api/config")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "storage-service"}
