"""Error tracking CRUD API.

Provides endpoints for centralized error management:
- GET  /                — list errors with optional filters (service, severity)
- GET  /stats           — aggregate statistics (total, last hour, by service)
- POST /report          — accept error reports from ErrorReporterMiddleware (no auth)
- POST /manual          — manually create an error report from UI form (auth required)
- POST /{id}/submit-issue — mark error as submitted to GitHub Issues
- DELETE /              — clear errors, optionally filtered by service

All authenticated endpoints require admin or superadmin role.
The /report endpoint is unauthenticated because it is called internally
by the ErrorReporterMiddleware during request processing.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User, ErrorRecord

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic schemas for request/response validation
# ---------------------------------------------------------------------------

class ErrorReportCreate(BaseModel):
    """Schema for incoming error reports from middleware or manual submission."""
    service: str = "unknown"
    severity: str = "error"
    category: str = ""
    message: str
    traceback: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    request_id: Optional[str] = None
    extra: Optional[str] = None


class ManualErrorCreate(BaseModel):
    """Schema for manually creating an error report from the UI form."""
    service: str = "linza-board"
    severity: str = "error"
    category: str = "ui"
    message: str
    description: str = ""
    submit_github: bool = False


class SubmitIssueRequest(BaseModel):
    """Schema for recording that an error was submitted to GitHub Issues."""
    github_issue_url: str


# ---------------------------------------------------------------------------
# Helper: require admin or superadmin role
# ---------------------------------------------------------------------------

def _require_manager(user: User) -> User:
    """Verify that the authenticated user has admin or superadmin role."""
    if user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user


# ---------------------------------------------------------------------------
# GET / — list errors with optional filtering
# ---------------------------------------------------------------------------

@router.get("/")
def list_errors(
    service: Optional[str] = Query(None, description="Filter by service name"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a paginated list of error records."""
    _require_manager(current_user)

    query = db.query(ErrorRecord)
    if service:
        query = query.filter(ErrorRecord.service == service)
    if severity:
        query = query.filter(ErrorRecord.severity == severity)

    total = query.count()
    errors = (
        query
        .order_by(ErrorRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

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
                "github_issue_url": e.github_issue_url,
                "status": e.status,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in errors
        ],
        "total": total,
    }


# ---------------------------------------------------------------------------
# GET /stats — aggregate error statistics
# ---------------------------------------------------------------------------

@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregate error statistics for the dashboard cards."""
    _require_manager(current_user)

    total = db.query(sa_func.count(ErrorRecord.id)).scalar() or 0

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    last_hour = (
        db.query(sa_func.count(ErrorRecord.id))
        .filter(ErrorRecord.created_at >= one_hour_ago)
        .scalar()
    ) or 0

    by_service_rows = (
        db.query(ErrorRecord.service, sa_func.count(ErrorRecord.id))
        .group_by(ErrorRecord.service)
        .all()
    )
    by_service = {row[0]: row[1] for row in by_service_rows}

    by_severity_rows = (
        db.query(ErrorRecord.severity, sa_func.count(ErrorRecord.id))
        .group_by(ErrorRecord.severity)
        .all()
    )
    by_severity = {row[0]: row[1] for row in by_severity_rows}

    return {
        "total": total,
        "last_hour": last_hour,
        "by_service": by_service,
        "by_severity": by_severity,
    }


# ---------------------------------------------------------------------------
# POST /report — accept error report (no auth, called by middleware)
# ---------------------------------------------------------------------------

@router.post("/report")
def report_error(
    body: ErrorReportCreate,
    db: Session = Depends(get_db),
):
    """Accept an error report and save it to the database.

    This endpoint does NOT require authentication because it is called
    internally by the ErrorReporterMiddleware during request processing.
    """
    record = ErrorRecord(
        service=body.service,
        severity=body.severity,
        category=body.category,
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


# ---------------------------------------------------------------------------
# POST /manual — manually create error report from UI form
# ---------------------------------------------------------------------------

@router.post("/manual")
def create_manual_error(
    body: ManualErrorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an error report manually from the Error Tracking page form.

    If submit_github is True, the response includes a pre-built GitHub
    Issue URL that the frontend can open in a new tab.
    """
    _require_manager(current_user)

    extra_text = body.description if body.description else None

    record = ErrorRecord(
        service=body.service,
        severity=body.severity,
        category=body.category,
        message=body.message,
        extra=extra_text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    result = {"id": record.id, "status": "recorded"}

    if body.submit_github:
        repo = "BigDataQueen/Linza-debug"
        title = f"[{body.service}] {body.message}"[:200]

        body_parts = [
            "## Error Report",
            "",
            f"**Service:** `{body.service}`",
            f"**Severity:** `{body.severity}`",
            f"**Category:** `{body.category}`" if body.category else None,
            f"**Reported by:** `{current_user.login}`",
            "",
            "## Message",
            "```",
            body.message,
            "```",
        ]

        if body.description:
            body_parts.extend(["", "## Description", "", body.description])

        body_parts.extend(["", "---", "*Reported manually from Linza Board error tracking interface.*"])

        issue_body = "\n".join(line for line in body_parts if line is not None)

        params = urlencode({
            "title": title,
            "body": issue_body,
            "labels": f"bug,{body.service}",
        })
        github_url = f"https://github.com/{repo}/issues/new?{params}"

        result["github_issue_url"] = github_url

    return result


# ---------------------------------------------------------------------------
# POST /{error_id}/submit-issue — mark error as submitted to GitHub
# ---------------------------------------------------------------------------

@router.post("/{error_id}/submit-issue")
def submit_issue(
    error_id: int,
    body: SubmitIssueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record that an error has been submitted as a GitHub Issue."""
    _require_manager(current_user)

    error = db.query(ErrorRecord).filter(ErrorRecord.id == error_id).first()
    if not error:
        raise HTTPException(status_code=404, detail="Error record not found")

    error.github_issue_url = body.github_issue_url
    error.status = "submitted"
    db.commit()
    return {"id": error.id, "status": "submitted", "github_issue_url": error.github_issue_url}


# ---------------------------------------------------------------------------
# DELETE / — clear error records
# ---------------------------------------------------------------------------

@router.delete("/")
def clear_errors(
    service: Optional[str] = Query(None, description="Clear only errors from this service"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete error records from the database."""
    _require_manager(current_user)

    query = db.query(ErrorRecord)
    if service:
        query = query.filter(ErrorRecord.service == service)

    count = query.count()
    query.delete(synchronize_session=False)
    db.commit()
    return {"deleted": count}
