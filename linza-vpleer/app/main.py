import asyncio
import contextvars
import logging

from pythonjsonlogger.json import JsonFormatter as JsonLogFormatter

_request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


class RequestIDFilter(logging.Filter):
    """Inject request_id from ContextVar into every log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx.get()
        return True
import os
import time
import traceback
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import (
    CACHE_CLEANUP_INTERVAL,
    CACHE_FILE_TTL,
    HTTP_CONNECT_TIMEOUT,
    HTTP_READ_TIMEOUT,
    MAX_CACHE_SIZE,
    TEMP_DIR,
)
from app.routes.metadata import router as metadata_router
from app.routes.player import router as player_router
from app.routes.stream import router as stream_router
from app.routes.timeline import router as timeline_router

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


configure_logging("vpleer")
logger = logging.getLogger("vpleer")

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
                        "service": "vpleer",
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
                        "service": "vpleer",
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


async def _background_cleanup():
    """Периодическая очистка кэша /tmp/vpleer."""
    while True:
        await asyncio.sleep(CACHE_CLEANUP_INTERVAL)
        try:
            if not os.path.isdir(TEMP_DIR):
                continue
            now = time.time()
            total_size = 0
            files_with_age = []
            for dirpath, _dirnames, filenames in os.walk(TEMP_DIR):
                for fname in filenames:
                    fpath = os.path.join(dirpath, fname)
                    try:
                        st = os.stat(fpath)
                        age = now - st.st_mtime
                        total_size += st.st_size
                        files_with_age.append((fpath, age, st.st_size))
                    except OSError:
                        continue
            # Удалить файлы старше TTL
            for fpath, age, fsize in files_with_age:
                if age > CACHE_FILE_TTL:
                    try:
                        os.remove(fpath)
                        total_size -= fsize
                        logger.info("Cache cleanup: removed %s (age=%ds)", fpath, int(age))
                    except OSError:
                        pass
            # Если всё ещё превышен лимит — удалять самые старые
            if total_size > MAX_CACHE_SIZE:
                files_with_age.sort(key=lambda x: -x[1])  # старые первые
                for fpath, age, fsize in files_with_age:
                    if total_size <= MAX_CACHE_SIZE:
                        break
                    try:
                        os.remove(fpath)
                        total_size -= fsize
                    except OSError:
                        pass
        except Exception as e:
            logger.error("Cache cleanup error: %s", e)


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Startup/shutdown: shared HTTP client и фоновая очистка."""
    app_instance.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(HTTP_CONNECT_TIMEOUT, read=HTTP_READ_TIMEOUT)
    )
    cleanup_task = asyncio.create_task(_background_cleanup())

    # Reconfigure uvicorn loggers → JSON via root handler (board#38)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True

    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    await app_instance.state.http_client.aclose()


app = FastAPI(
    title="Linza VPleer",
    description="Сервис видеоплеера: воспроизведение, навигация и просмотр видеофайлов",
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

app.mount("/api/vpleer/static", StaticFiles(directory="app/static"), name="vpleer-static")

app.include_router(stream_router)
app.include_router(metadata_router)
app.include_router(timeline_router)
app.include_router(player_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "vpleer"}
