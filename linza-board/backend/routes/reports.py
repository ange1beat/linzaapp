"""Analysis reports CRUD API."""

import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend import video_ai_filter_client
from backend.auth import PORTAL_OPERATOR, get_current_user, oauth2_scheme, resolve_active_role
from backend.database import get_db
from backend.models import User, AnalysisReport

router = APIRouter()

_VAF_JOB_UUID = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class ReportCreate(BaseModel):
    filename: str
    report_name: str = ""
    source: str = ""
    started_at: str = ""
    finished_at: str = ""
    match_count: int = 0
    status: str = "success"
    report_json: str = "{}"


VALID_CONTENT_MARKING = frozenset({"clean", "age_12", "age_16", "age_18", "banned"})

def _active_portal_role(token: str | None, user: User) -> str | None:
    return resolve_active_role(user, token)


def _operator_marking_locked(report: AnalysisReport) -> bool:
    return bool(getattr(report, "revision_done", False)) or bool(getattr(report, "escalated", False))


def _assert_operator_may_change_marking(report: AnalysisReport, token: str | None, user: User) -> None:
    if _active_portal_role(token, user) != PORTAL_OPERATOR:
        return
    if _operator_marking_locked(report):
        raise HTTPException(
            status_code=403,
            detail="Маркировку после ревизии или при передаче юристу может менять только юрист, главный редактор или администратор портала.",
        )


def _assert_operator_may_clear_revision(report: AnalysisReport, token: str | None, user: User) -> None:
    if _active_portal_role(token, user) != PORTAL_OPERATOR:
        return
    if bool(getattr(report, "revision_done", False)):
        raise HTTPException(
            status_code=403,
            detail="Снять отметку ревизии может только юрист, главный редактор или администратор портала.",
        )


def _assert_operator_may_deescalate(token: str | None, user: User) -> None:
    if _active_portal_role(token, user) != PORTAL_OPERATOR:
        return
    raise HTTPException(
        status_code=403,
        detail="Снять эскалацию (вернуть с рассмотрения юриста) может только юрист, главный редактор или администратор портала.",
    )


class ReportPatch(BaseModel):
    """Частичное обновление отчёта (например привязка к ключу видео в хранилище)."""

    filename: str | None = None
    report_name: str | None = None
    source: str | None = None
    content_marking: str | None = None  # clean | age_12 | age_16 | age_18 | banned | "" сброс
    revision_done: bool | None = None
    escalated: bool | None = None


class ReportResponse(BaseModel):
    id: int
    filename: str
    report_name: str
    source: str
    started_at: str
    finished_at: str
    match_count: int
    status: str
    content_marking: str | None = None
    revision_done: bool = False
    escalated: bool = False
    created_at: str | None = None

    class Config:
        from_attributes = True


def _report_row(r: AnalysisReport) -> dict:
    return {
        "id": r.id,
        "filename": r.filename,
        "report_name": r.report_name,
        "source": r.source,
        "started_at": r.started_at,
        "finished_at": r.finished_at,
        "match_count": r.match_count,
        "status": r.status,
        "content_marking": getattr(r, "content_marking", None),
        "revision_done": bool(getattr(r, "revision_done", False)),
        "escalated": bool(getattr(r, "escalated", False)),
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@router.get("/")
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reports = db.query(AnalysisReport).order_by(AnalysisReport.id.desc()).all()
    return [_report_row(r) for r in reports]


@router.get("/vaf-pdf/{job_id}")
def download_vaf_pdf(
    job_id: str,
    _: User = Depends(get_current_user),
):
    """Прокси PDF из video-ai-filter по UUID задачи (поле jobId в сохранённом отчёте)."""
    jid = (job_id or "").strip()
    if not _VAF_JOB_UUID.match(jid):
        raise HTTPException(400, "Некорректный идентификатор задачи")
    if not video_ai_filter_client.api_base():
        raise HTTPException(503, "Сервис video-ai-filter не настроен (VIDEO_AI_FILTER_BASE_URL)")
    try:
        pdf = video_ai_filter_client.fetch_job_pdf_bytes(jid)
    except Exception as e:
        raise HTTPException(502, str(e)[:800]) from e
    fname = f"linza-report-{jid[:8]}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.post("/")
def create_report(body: ReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = AnalysisReport(
        filename=body.filename,
        report_name=body.report_name,
        source=body.source,
        started_at=body.started_at,
        finished_at=body.finished_at,
        match_count=body.match_count,
        status=body.status,
        report_json=body.report_json,
        created_by=current_user.id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"id": report.id, "filename": report.filename}


@router.patch("/{report_id}")
def patch_report(
    report_id: int,
    body: ReportPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str | None = Depends(oauth2_scheme),
):
    report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    if (
        body.filename is None
        and body.report_name is None
        and body.source is None
        and body.content_marking is None
        and body.revision_done is None
        and body.escalated is None
    ):
        raise HTTPException(400, "No fields to update")
    if body.filename is not None:
        report.filename = body.filename
    if body.report_name is not None:
        report.report_name = body.report_name
    if body.source is not None:
        report.source = body.source
    if body.content_marking is not None:
        _assert_operator_may_change_marking(report, token, current_user)
        v = (body.content_marking or "").strip()
        if not v:
            report.content_marking = None
        elif v not in VALID_CONTENT_MARKING:
            raise HTTPException(400, f"content_marking: допустимо {sorted(VALID_CONTENT_MARKING)}")
        else:
            report.content_marking = v
    if body.revision_done is not None:
        if body.revision_done is False:
            _assert_operator_may_clear_revision(report, token, current_user)
        report.revision_done = body.revision_done
    if body.escalated is not None:
        if body.escalated is False:
            _assert_operator_may_deescalate(token, current_user)
        report.escalated = body.escalated
    db.commit()
    db.refresh(report)
    return _report_row(report)


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    return {
        **_report_row(report),
        "report_json": report.report_json,
    }


@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    db.delete(report)
    db.commit()
    return {"status": "deleted"}
