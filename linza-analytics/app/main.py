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
import traceback
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

import os

import app.config as config
from app.config import CORS_ORIGINS, ERROR_TRACKER_URL

SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "")
from app.db import init_db
from app.routes import classifier

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


configure_logging("analytics-service")
logger = logging.getLogger("analytics-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Database path: %s", config.DATABASE_PATH)
    init_db()

    # Reconfigure uvicorn loggers → JSON via root handler (board#38)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True

    yield


app = FastAPI(
    title="Linza Analytics Service",
    description="Сервис аналитики: классификатор нарушений, анализ результатов обработки видео и отчёты",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        request.state.request_id = request_id
        _request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error("[%s] Unhandled exception: %s", request_id, exc, exc_info=True)
            try:
                _h = {"X-Service-Key": SERVICE_API_KEY} if SERVICE_API_KEY else {}
                async with httpx.AsyncClient(timeout=5) as client:
                    await client.post(f"{ERROR_TRACKER_URL}/api/errors/report", headers=_h, json={
                        "service": "analytics-service",
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
                        "service": "analytics-service",
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


app.add_middleware(ErrorReporterMiddleware)
app.add_middleware(ServiceKeyMiddleware)

app.include_router(classifier.router, prefix="/api/classifier")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "analytics-service"}
