"""Linza Debug — Error Tracker Service.

Minimal FastAPI service that receives error reports from all
Linza platform microservices via POST /api/errors/report.

Stores errors in a local SQLite database and provides
API endpoints for querying, filtering and dashboard statistics.

Port: 8004 (default)
"""

import contextvars
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pythonjsonlogger.json import JsonFormatter as JsonLogFormatter
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, func, text
from sqlalchemy.orm import declarative_base, sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


class RequestIDFilter(logging.Filter):
    """Inject request_id from ContextVar into every log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx.get()
        return True

# ---------------------------------------------------------------------------
# Category auto-inference
# ---------------------------------------------------------------------------

VALID_CATEGORIES = ("ui", "api", "storage", "auth", "player", "analytics", "network")

SERVICE_CATEGORY_MAP: dict[str, str] = {
    "analytics-service": "analytics",
    "storage-service": "storage",
    "vpleer": "player",
    "linza-board": "api",
    "error-tracker": "api",
}

DEFAULT_CATEGORY = "api"


def infer_category(service: str, explicit: str | None = None) -> str:
    """Return explicit category if provided, otherwise infer from service name."""
    if explicit:
        return explicit
    return SERVICE_CATEGORY_MAP.get(service, DEFAULT_CATEGORY)

# ---------------------------------------------------------------------------
# Database setup (SQLite)
# ---------------------------------------------------------------------------

DB_PATH = os.getenv("ERROR_DB_PATH", "/app/data/errors.db")
os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ErrorRecord(Base):
    """Error record stored by the tracker."""
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, nullable=False, default="unknown")
    severity = Column(String, nullable=False, default="error")
    category = Column(String, nullable=False, default="api")
    message = Column(Text, nullable=False)
    traceback = Column(Text, default=None)
    endpoint = Column(String, default=None)
    method = Column(String, default=None)
    status_code = Column(Integer, default=None)
    request_id = Column(String, default=None)
    extra = Column(Text, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(bind=engine)

# Migrate: add category column if missing (create_all does not alter existing tables)
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE errors ADD COLUMN category TEXT NOT NULL DEFAULT 'api'"))
        conn.commit()
except Exception:
    pass  # column already exists

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ErrorReportCreate(BaseModel):
    """Incoming error report from a microservice middleware."""
    service: str = "unknown"
    severity: str = "error"
    category: Optional[str] = None
    message: str
    traceback: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    request_id: Optional[str] = None
    extra: Optional[str] = None

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "")


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


configure_logging("error-tracker")

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    # Reconfigure uvicorn loggers → JSON via root handler (board#38)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True
    yield


app = FastAPI(title="Linza Error Tracker", version="1.0.0", lifespan=lifespan)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Extract or generate X-Request-ID and store in ContextVar (board#39)."""
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())[:8]
        _request_id_ctx.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class ServiceKeyMiddleware(BaseHTTPMiddleware):
    """Validate X-Service-Key header for inter-service auth."""
    async def dispatch(self, request, call_next):
        if not SERVICE_API_KEY:
            return await call_next(request)
        if request.url.path == "/health":
            return await call_next(request)
        key = request.headers.get("x-service-key", "")
        if key != SERVICE_API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing service key"})
        return await call_next(request)


app.add_middleware(RequestIDMiddleware)
app.add_middleware(ServiceKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    """Health check for container orchestration."""
    return {"status": "ok", "service": "error-tracker"}


@app.post("/api/errors/report")
def report_error(body: ErrorReportCreate):
    """Accept error report from any microservice."""
    db = SessionLocal()
    try:
        record = ErrorRecord(
            service=body.service,
            severity=body.severity,
            category=infer_category(body.service, body.category),
            message=body.message,
            traceback=body.traceback,
            endpoint=body.endpoint,
            method=body.method,
            status_code=body.status_code,
            request_id=body.request_id,
            extra=body.extra,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"id": record.id, "status": "recorded"}
    finally:
        db.close()


@app.get("/api/errors")
def list_errors(
    service: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    request_id: Optional[str] = Query(None),
    endpoint: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None, description="ISO 8601 datetime, e.g. 2026-04-01T00:00:00"),
    to_date: Optional[str] = Query(None, description="ISO 8601 datetime, e.g. 2026-04-02T23:59:59"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List error records with optional filters."""
    db = SessionLocal()
    try:
        query = db.query(ErrorRecord)
        if service:
            query = query.filter(ErrorRecord.service == service)
        if severity:
            query = query.filter(ErrorRecord.severity == severity)
        if category:
            query = query.filter(ErrorRecord.category == category)
        if request_id:
            query = query.filter(ErrorRecord.request_id == request_id)
        if endpoint:
            query = query.filter(ErrorRecord.endpoint.contains(endpoint))
        if from_date:
            try:
                dt = datetime.fromisoformat(from_date)
                if dt.tzinfo is not None:
                    dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                query = query.filter(ErrorRecord.created_at >= dt)
            except ValueError:
                pass
        if to_date:
            try:
                dt = datetime.fromisoformat(to_date)
                if dt.tzinfo is not None:
                    dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                query = query.filter(ErrorRecord.created_at <= dt)
            except ValueError:
                pass
        total = query.count()
        errors = query.order_by(ErrorRecord.created_at.desc()).offset(offset).limit(limit).all()
        return {
            "errors": [
                {
                    "id": e.id,
                    "service": e.service,
                    "severity": e.severity,
                    "category": e.category,
                    "message": e.message,
                    "traceback": e.traceback,
                    "endpoint": e.endpoint,
                    "method": e.method,
                    "status_code": e.status_code,
                    "request_id": e.request_id,
                    "extra": e.extra,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in errors
            ],
            "total": total,
        }
    finally:
        db.close()


@app.get("/api/dashboard")
def dashboard():
    """Dashboard statistics for the error tracker."""
    db = SessionLocal()
    try:
        total = db.query(func.count(ErrorRecord.id)).scalar() or 0
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        last_hour = (
            db.query(func.count(ErrorRecord.id))
            .filter(ErrorRecord.created_at >= one_hour_ago)
            .scalar()
        ) or 0
        by_service = dict(
            db.query(ErrorRecord.service, func.count(ErrorRecord.id))
            .group_by(ErrorRecord.service)
            .all()
        )
        by_severity = dict(
            db.query(ErrorRecord.severity, func.count(ErrorRecord.id))
            .group_by(ErrorRecord.severity)
            .all()
        )
        by_category = dict(
            db.query(ErrorRecord.category, func.count(ErrorRecord.id))
            .group_by(ErrorRecord.category)
            .all()
        )
        return {
            "total": total,
            "last_hour": last_hour,
            "by_service": by_service,
            "by_severity": by_severity,
            "by_category": by_category,
        }
    finally:
        db.close()
