"""Linza Board — FastAPI application entry point.

This module configures the FastAPI app, registers all API routers,
sets up CORS, and includes the ErrorReporterMiddleware that captures
HTTP errors and unhandled exceptions for centralized error tracking.

The middleware saves errors both to the local SQLite database (for the
UI error tracking page) and optionally forwards them to an external
error-tracker service (Linza Debug) if ERROR_TRACKER_URL is configured.
"""

import asyncio
import contextvars
import logging
import os

from pythonjsonlogger.json import JsonFormatter as JsonLogFormatter

_request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


class RequestIDFilter(logging.Filter):
    """Inject request_id from ContextVar into every log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx.get()
        return True


class _SkipMiddlewareLoggerFilter(logging.Filter):
    """Skip records from ErrorReporterMiddleware logger (already tracked)."""
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name != "linza.error_reporter"


# board#40: Async error tracker queue (Variant C)
# ErrorTrackerHandler.emit() → asyncio.Queue → background consumer → DB + forward
_error_tracker_queue: asyncio.Queue | None = None


class ErrorTrackerHandler(logging.Handler):
    """Bridge: logger.error()/critical() → asyncio.Queue → DB + external tracker.

    Variant C (board#40): emit() serializes the record and enqueues it.
    A background consumer task (started in lifespan) processes items:
      Stage 1: Save ErrorRecord to local DB
      Stage 2: Forward to external error-tracker (if ERROR_TRACKER_URL is set)

    Do NOT override filter() — it breaks addFilter() chain.
    """

    def __init__(self, service_name: str):
        super().__init__(level=logging.ERROR)
        self.service_name = service_name

    def emit(self, record: logging.LogRecord) -> None:
        if _error_tracker_queue is None:
            return  # Consumer not started yet (pre-lifespan)
        try:
            import traceback as tb_mod

            severity = "critical" if record.levelno >= logging.CRITICAL else "error"
            traceback_str = None
            if record.exc_info and record.exc_info[1] is not None:
                traceback_str = "".join(tb_mod.format_exception(*record.exc_info))

            _error_tracker_queue.put_nowait({
                "service": self.service_name,
                "severity": severity,
                "message": record.getMessage(),
                "traceback": traceback_str,
                "request_id": getattr(record, "request_id", None) or "",
            })
        except asyncio.QueueFull:
            self.handleError(record)
        except Exception:
            self.handleError(record)
import traceback
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

# Подхватить linza-board/.env до любых импортов backend.* (там os.getenv при загрузке модулей).
_board_root = Path(__file__).resolve().parent.parent
load_dotenv(_board_root / ".env")
load_dotenv()

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from backend.database import Base, engine, SessionLocal, run_migrations, run_sqlite_migrations
from backend.auth import seed_superadmin
from backend.routes import auth, storage, users, reports, access, sources, errors, analysis_queue, detector_fetch, portal
from backend.routes import storage_import, yandex_oauth, google_oauth
from backend.routes import tenants, teams, storage_quotas, projects

SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "")

# Register all models on Base.metadata before create_all (startup)
import backend.models  # noqa: F401


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

    # board#40: Bridge logger.error()/critical() → ErrorRecord in local DB
    tracker_handler = ErrorTrackerHandler(service_name)
    tracker_handler.addFilter(RequestIDFilter())
    tracker_handler.addFilter(_SkipMiddlewareLoggerFilter())
    logging.root.addHandler(tracker_handler)


configure_logging("linza-board")

# Logger for error reporting subsystem
logger = logging.getLogger("linza.error_reporter")

# Optional URL of external error-tracker service (Linza Debug).
# If not set, errors are only saved to the local database.
ERROR_TRACKER_URL = os.getenv("ERROR_TRACKER_URL", "").rstrip("/") or None

# HTTP status codes that should NOT be recorded by the middleware.
# These are normal operational responses, not real errors:
# 401 = expired/missing JWT token (normal auth flow)
# 404 = missing route or static file (noise in production)
# 405 = wrong HTTP method (client-side bug, not server error)
_IGNORED_STATUS_CODES = {401, 404, 405}


async def _error_tracker_consumer():
    """Background consumer: drains _error_tracker_queue → local DB + external POST.

    Runs as an asyncio.Task started in lifespan. Processes items from
    ErrorTrackerHandler.emit() in two stages (same as _report_error):
      Stage 1: Save to local ErrorRecord table
      Stage 2: Forward to external error-tracker (Linza Debug) if configured
    Stops when it receives a None sentinel (shutdown).
    """
    while True:
        data = await _error_tracker_queue.get()
        if data is None:  # shutdown sentinel
            break
        # Stage 1: Save to local database
        try:
            from backend.models import ErrorRecord
            db = SessionLocal()
            try:
                db.add(ErrorRecord(
                    service=data["service"],
                    severity=data["severity"],
                    message=data["message"],
                    traceback=data["traceback"],
                    request_id=data["request_id"],
                ))
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.debug("ErrorTrackerHandler: DB save failed: %s", e)

        # Stage 2: Forward to external error-tracker
        if ERROR_TRACKER_URL:
            try:
                svc_headers = {"X-Service-Key": SERVICE_API_KEY} if SERVICE_API_KEY else {}
                async with httpx.AsyncClient(timeout=5) as client:
                    await client.post(
                        f"{ERROR_TRACKER_URL}/api/errors/report",
                        json=data,
                        headers=svc_headers,
                    )
            except Exception as e:
                logger.debug("ErrorTrackerHandler: forward failed: %s", e)


async def _report_error(service: str, message: str,
                        severity: str = "error",
                        traceback_str: str = None,
                        endpoint: str = None,
                        method: str = None,
                        status_code: int = None,
                        request_id: str = None,
                        extra: str = None):
    """Save error to local database and optionally forward to external tracker.

    This function is called by ErrorReporterMiddleware when it intercepts
    HTTP errors (4xx/5xx) or unhandled exceptions during request processing.

    Two-stage error recording:
    1. Save to local SQLite DB (error_records table) — always attempted
    2. Forward to external Linza Debug service — only if ERROR_TRACKER_URL is set

    Args:
        service:       name of the originating service (e.g. 'linza-board')
        message:       human-readable error description
        severity:      error level — critical / error / warning / info
        traceback_str: full Python traceback (for unhandled exceptions)
        endpoint:      HTTP path where the error occurred
        method:        HTTP method (GET, POST, etc.)
        status_code:   HTTP response status code
        request_id:    unique request ID for log correlation
        extra:         additional context as JSON string
    """
    # --- Stage 1: Save to local database ---
    # Lazy import to avoid circular dependency (main.py -> routes -> models)
    try:
        from backend.models import ErrorRecord
        db = SessionLocal()
        try:
            record = ErrorRecord(
                service=service,
                severity=severity,
                message=message,
                traceback=traceback_str,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                request_id=request_id,
                extra=extra,
            )
            db.add(record)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.debug("Failed to save error to local DB: %s", e)

    # --- Stage 2: Forward to external error-tracker (Linza Debug) ---
    if not ERROR_TRACKER_URL:
        return

    payload = {
        "service": service,
        "severity": severity,
        "message": message,
        "traceback": traceback_str,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "request_id": request_id,
        "extra": extra,
    }

    try:
        svc_headers = {"X-Service-Key": SERVICE_API_KEY} if SERVICE_API_KEY else {}
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(f"{ERROR_TRACKER_URL}/api/errors/report", json=payload, headers=svc_headers)
    except Exception as e:
        logger.debug("Failed to report error to tracker: %s", e)


class ErrorReporterMiddleware(BaseHTTPMiddleware):
    """Middleware that intercepts errors and reports them to error tracking.

    Captures three categories of events:
    - Unhandled exceptions (severity: critical, status 500)
    - HTTP 5xx responses (severity: error)
    - HTTP 4xx responses (severity: warning) — except 401, 404, 405

    Ignored status codes (not recorded to avoid noise):
    - 401: expired/missing JWT token (normal auth flow)
    - 404: missing routes or static files
    - 405: wrong HTTP method

    Each captured event is passed to _report_error() which saves it
    to the local DB and optionally forwards to the external tracker.

    Constructor args:
        app:          the ASGI application instance
        service_name: identifier for this service in error reports
    """

    def __init__(self, app, service_name: str = "unknown"):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process each request and capture errors.

        Generates a short UUID request_id for log correlation,
        then delegates to the next middleware/handler. If the handler
        raises an exception or returns a 4xx/5xx status, the error
        is reported via _report_error().
        """
        # Preserve incoming X-Request-ID or generate new one
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        _request_id_ctx.set(request_id)

        try:
            response = await call_next(request)
        except Exception as exc:
            # Unhandled exception — critical severity
            tb = traceback.format_exc()
            logger.error("[%s] Unhandled exception: %s", request_id, exc, exc_info=True)

            await _report_error(
                service=self.service_name,
                message=str(exc),
                severity="critical",
                traceback_str=tb,
                endpoint=str(request.url.path),
                method=request.method,
                status_code=500,
                request_id=request_id,
            )

            resp = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
            resp.headers["X-Request-ID"] = request_id
            return resp

        # Skip ignored status codes (normal operational responses)
        if response.status_code in _IGNORED_STATUS_CODES:
            response.headers["X-Request-ID"] = request_id
            return response

        # HTTP 5xx — server error
        if response.status_code >= 500:
            await _report_error(
                service=self.service_name,
                message=f"HTTP {response.status_code} on {request.method} {request.url.path}",
                severity="error",
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                request_id=request_id,
            )
        # HTTP 4xx — client error (excluding ignored codes above)
        elif response.status_code >= 400:
            await _report_error(
                service=self.service_name,
                message=f"HTTP {response.status_code} on {request.method} {request.url.path}",
                severity="warning",
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                request_id=request_id,
            )

        response.headers["X-Request-ID"] = request_id
        return response


# ---------------------------------------------------------------------------
# FastAPI application setup
# ---------------------------------------------------------------------------

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database schema, seed superadmin, migrate credentials.

    PostgreSQL: Alembic migrations (alembic upgrade head).
    SQLite (dev/test): Base.metadata.create_all().
    """
    run_migrations()
    run_sqlite_migrations()
    db = SessionLocal()
    try:
        seed_superadmin(db)
        _migrate_plaintext_credentials(db)
    finally:
        db.close()

    # Reconfigure uvicorn loggers → JSON via root handler (board#38)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True

    # board#40: Start error tracker consumer (Variant C — asyncio queue)
    global _error_tracker_queue
    _error_tracker_queue = asyncio.Queue(maxsize=1000)
    consumer_task = asyncio.create_task(_error_tracker_consumer())

    yield

    # Shutdown: drain queue and stop consumer
    await _error_tracker_queue.put(None)  # sentinel
    await consumer_task
    _error_tracker_queue = None


app = FastAPI(title="Linza Board", version="1.0.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow frontend dev server and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error tracking middleware — intercepts all HTTP errors
app.add_middleware(ErrorReporterMiddleware, service_name="linza-board")

# --- API routers ---
app.include_router(auth.router, prefix="/api/auth")          # authentication
app.include_router(portal.router, prefix="/api/portal")      # PRD: мастер администратора (org-config)
app.include_router(users.router, prefix="/api/users")        # user management
app.include_router(storage.router, prefix="/api/settings/storage")  # S3 storage profiles
app.include_router(reports.router, prefix="/api/reports")    # analysis reports
app.include_router(access.router, prefix="/api/settings/access")    # access credentials
app.include_router(sources.router, prefix="/api/settings/sources")  # data sources
app.include_router(errors.router, prefix="/api/errors")      # error tracking
app.include_router(tenants.router, prefix="/api/tenants")    # multi-tenancy
app.include_router(teams.router, prefix="/api/teams")        # team management
app.include_router(storage_quotas.router, prefix="/api/storage")  # storage quotas
app.include_router(projects.router, prefix="/api/projects")  # projects & sharing
app.include_router(detector_fetch.router, prefix="/api")
app.include_router(analysis_queue.router, prefix="/api/analysis-queue")
app.include_router(yandex_oauth.router, prefix="/api/integrations/yandex")
app.include_router(google_oauth.router, prefix="/api/integrations/google")
# До catch-all-прокси: маршруты по сохранённому S3-профилю и личному Яндекс.Диску.
app.include_router(storage_import.router, prefix="/api/files")

# Same-origin /api/files и /api/config — прокси на Linza-storage-service.
# Явный STORAGE_SERVICE_URL имеет приоритет; иначе: в Docker — storage-service, локально — 127.0.0.1:8001.
def _resolve_storage_proxy_base() -> str:
    raw = os.getenv("STORAGE_SERVICE_URL", "").strip()
    if raw:
        return raw.rstrip("/")
    if os.path.exists("/.dockerenv"):
        return "http://storage-service:8001"
    return "http://127.0.0.1:8001"


STORAGE_PROXY_BASE = _resolve_storage_proxy_base()

_PROXY_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]


def _resolve_analytics_proxy_base() -> str:
    """Куда проксировать /api/classifier с процесса board.

    Приоритет: ANALYTICS_SERVICE_URL. В Docker без переменной — как у storage:
    hostname сервиса compose (analytics-service:8002), не 127.0.0.1 (это сам контейнер board).

    Единый контейнер Linza-deploy: entrypoint выставляет ANALYTICS_SERVICE_URL=http://127.0.0.1:8002
    *до* запуска uvicorn board — тогда срабатывает ветка выше.
    """
    raw = os.getenv("ANALYTICS_SERVICE_URL", "").strip()
    if raw:
        return raw.rstrip("/")
    if os.path.exists("/.dockerenv"):
        return "http://analytics-service:8002"
    return "http://127.0.0.1:8002"


ANALYTICS_PROXY_BASE = _resolve_analytics_proxy_base()


def _resolve_vpleer_proxy_base() -> str:
    """Куда проксировать /api/vpleer (встроенный HTML-плеер и stream).

    Без прокси запросы с одного origin (board + dist) попадают в SPA catch-all и дают 404.
    """
    raw = os.getenv("VPLEER_SERVICE_URL", "").strip()
    if raw:
        return raw.rstrip("/")
    if os.path.exists("/.dockerenv"):
        return "http://vpleer-service:8003"
    return "http://127.0.0.1:8003"


VPLEER_PROXY_BASE = _resolve_vpleer_proxy_base()


async def _proxy_to_analytics_service(request: Request) -> Response:
    target = ANALYTICS_PROXY_BASE + request.url.path
    if request.url.query:
        target += "?" + request.url.query
    body = await request.body()
    hop = {
        "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "upgrade", "host",
    }
    headers = {k: v for k, v in request.headers.items() if k.lower() not in hop}
    if SERVICE_API_KEY:
        headers["X-Service-Key"] = SERVICE_API_KEY
    if hasattr(request.state, "request_id"):
        headers["X-Request-ID"] = request.state.request_id
    timeout = httpx.Timeout(120.0, connect=30.0)
    client = httpx.AsyncClient(timeout=timeout)
    try:
        upstream_req = client.build_request(
            request.method,
            target,
            headers=headers,
            content=body if body else None,
        )
        upstream = await client.send(upstream_req, stream=True)
    except httpx.RequestError as exc:
        await client.aclose()
        return JSONResponse(
            {"detail": f"analytics-service недоступен: {exc}"},
            status_code=502,
        )

    drop = {"connection", "transfer-encoding", "content-encoding"}
    out_hdr = {
        k: v
        for k, v in upstream.headers.items()
        if k.lower() not in drop
    }

    async def closing_stream():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(
        closing_stream(),
        status_code=upstream.status_code,
        headers=out_hdr,
    )


async def _proxy_to_storage_service(request: Request) -> Response:
    target = STORAGE_PROXY_BASE + request.url.path
    if request.url.query:
        target += "?" + request.url.query
    body = await request.body()
    hop = {
        "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "upgrade", "host",
    }
    headers = {k: v for k, v in request.headers.items() if k.lower() not in hop}
    if SERVICE_API_KEY:
        headers["X-Service-Key"] = SERVICE_API_KEY
    if hasattr(request.state, "request_id"):
        headers["X-Request-ID"] = request.state.request_id
    timeout = httpx.Timeout(600.0, connect=30.0)
    client = httpx.AsyncClient(timeout=timeout)
    try:
        upstream_req = client.build_request(
            request.method,
            target,
            headers=headers,
            content=body if body else None,
        )
        upstream = await client.send(upstream_req, stream=True)
    except httpx.RequestError as exc:
        await client.aclose()
        return JSONResponse(
            {"detail": f"storage-service недоступен: {exc}"},
            status_code=502,
        )

    drop = {"connection", "transfer-encoding", "content-encoding"}
    # Starlette StreamingResponse ожидает headers как Mapping (dict), не list[tuple]
    out_hdr = {
        k: v
        for k, v in upstream.headers.items()
        if k.lower() not in drop
    }

    async def closing_stream():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(
        closing_stream(),
        status_code=upstream.status_code,
        headers=out_hdr,
    )


async def _proxy_to_vpleer_service(request: Request) -> Response:
    target = VPLEER_PROXY_BASE + request.url.path
    if request.url.query:
        target += "?" + request.url.query
    body = await request.body()
    hop = {
        "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "upgrade", "host",
    }
    headers = {k: v for k, v in request.headers.items() if k.lower() not in hop}
    timeout = httpx.Timeout(600.0, connect=30.0)
    client = httpx.AsyncClient(timeout=timeout)
    try:
        upstream_req = client.build_request(
            request.method,
            target,
            headers=headers,
            content=body if body else None,
        )
        upstream = await client.send(upstream_req, stream=True)
    except httpx.RequestError as exc:
        await client.aclose()
        return JSONResponse(
            {"detail": f"vpleer-service недоступен: {exc}"},
            status_code=502,
        )

    drop = {"connection", "transfer-encoding", "content-encoding"}
    out_hdr = {
        k: v
        for k, v in upstream.headers.items()
        if k.lower() not in drop
    }

    async def closing_stream():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(
        closing_stream(),
        status_code=upstream.status_code,
        headers=out_hdr,
    )


def _check_storage_quota(request: Request) -> None:
    """Check if the user has sufficient storage quota before upload.

    Only applies to POST requests (file uploads). Raises HTTPException
    if quota is exceeded at any level (user, team, tenant).
    """
    if request.method != "POST":
        return

    token = request.headers.get("authorization", "").replace("Bearer ", "")
    if not token:
        return

    try:
        from backend.auth import decode_access_token
        payload = decode_access_token(token)
    except Exception:
        return

    from backend.models import StorageQuota, User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.login == payload.get("sub")).first()
        if not user:
            return

        for scope_type, scope_id in [
            ("user", user.id),
            ("team", user.team_id),
            ("tenant", user.tenant_id),
        ]:
            if not scope_id:
                continue
            quota = db.query(StorageQuota).filter(
                StorageQuota.scope_type == scope_type,
                StorageQuota.scope_id == scope_id,
            ).first()
            if quota and quota.quota_bytes > 0 and (quota.used_bytes or 0) >= quota.quota_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"Квота хранилища исчерпана ({scope_type})",
                )
    finally:
        db.close()


@app.api_route("/api/files", methods=_PROXY_METHODS, include_in_schema=False)
@app.api_route("/api/files/{rest_path:path}", methods=_PROXY_METHODS, include_in_schema=False)
async def proxy_storage_files(request: Request):
    _check_storage_quota(request)
    return await _proxy_to_storage_service(request)


@app.api_route("/api/config", methods=_PROXY_METHODS, include_in_schema=False)
@app.api_route("/api/config/{rest_path:path}", methods=_PROXY_METHODS, include_in_schema=False)
async def proxy_storage_config(request: Request):
    return await _proxy_to_storage_service(request)


@app.api_route("/api/classifier", methods=_PROXY_METHODS, include_in_schema=False)
@app.api_route("/api/classifier/", methods=_PROXY_METHODS, include_in_schema=False)
@app.api_route("/api/classifier/{rest_path:path}", methods=_PROXY_METHODS, include_in_schema=False)
async def proxy_analytics_classifier(request: Request):
    return await _proxy_to_analytics_service(request)


@app.api_route("/api/vpleer", methods=_PROXY_METHODS, include_in_schema=False)
@app.api_route("/api/vpleer/{rest_path:path}", methods=_PROXY_METHODS, include_in_schema=False)
async def proxy_vpleer(request: Request):
    return await _proxy_to_vpleer_service(request)


def _migrate_plaintext_credentials(db):
    """Encrypt any AccessCredential passwords still stored as plaintext."""
    from backend.encryption import encrypt_password, _FERNET_PREFIX
    from backend.models import AccessCredential
    migrated = 0
    for cred in db.query(AccessCredential).all():
        if cred.password_encrypted and not cred.password_encrypted.startswith(_FERNET_PREFIX):
            cred.password_encrypted = encrypt_password(cred.password_encrypted)
            migrated += 1
    if migrated:
        db.commit()
        logger.info("Migrated %d plaintext credential(s) to Fernet encryption", migrated)




@app.get("/health")
async def health():
    """Health check endpoint for container orchestration."""
    return {"status": "ok", "service": "linza-board"}


# ---------------------------------------------------------------------------
# Serve Vue SPA static files in production
# ---------------------------------------------------------------------------
_dist = Path("dist")
if _dist.exists():
    # Mount the Vite-built assets directory
    app.mount("/assets", StaticFiles(directory=str(_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        """Serve Vue SPA — return index.html for all non-API, non-asset routes."""
        if full_path.startswith("api/"):
            raise HTTPException(404, detail="Not Found")
        candidate = _dist / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_dist / "index.html")
