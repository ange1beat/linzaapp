"""Портал PRD: org-config, метрики из БД (без фиктивных данных), юрист, команда."""

import json
from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session

from backend.auth import (
    PORTAL_ADMINISTRATOR,
    PORTAL_CHIEF_EDITOR,
    PORTAL_LAWYER,
    get_current_user,
    oauth2_scheme,
    portal_roles_for_user,
    resolve_active_role,
)
from backend.database import get_db
from backend.models import AnalysisReport, AppSetting, User, VideoAnalysisQueueItem
from backend.org_portal_sources import ORG_CONFIG_KEY, get_sources_enabled

router = APIRouter()

PERIOD_DAYS = {"week": 7, "month": 30, "quarter": 91, "year": 365}

MARKING_LABELS = {
    "clean": ("Чисто (0+)", "#2cd494"),
    "age_12": ("12+", "#38c0d4"),
    "age_16": ("16+", "#6898e8"),
    "age_18": ("18+", "#d4b838"),
    "banned": ("Запрещено", "#e45878"),
    "unclassified": ("Не задана", "#64748b"),
}


def _period_cutoff(period: str) -> datetime:
    days = PERIOD_DAYS.get(period, 30)
    return datetime.utcnow() - timedelta(days=days)


class OrgPortalConfigBody(BaseModel):
    data: dict


def _require_administrator(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
) -> User:
    if resolve_active_role(current_user, token) != PORTAL_ADMINISTRATOR:
        raise HTTPException(status_code=403, detail="Нужна роль «Администратор» портала")
    return current_user


def _require_chief_editor(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
) -> User:
    if resolve_active_role(current_user, token) != PORTAL_CHIEF_EDITOR:
        raise HTTPException(status_code=403, detail="Нужна роль «Главный редактор»")
    return current_user


def _require_lawyer(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
) -> User:
    if resolve_active_role(current_user, token) != PORTAL_LAWYER:
        raise HTTPException(status_code=403, detail="Нужна роль «Юрист»")
    return current_user


@router.get("/ingest-sources")
def get_ingest_sources(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Какие вкладки «Добавить файлы» разрешены (org-config). Доступно всем авторизованным."""
    return {"sources_enabled": get_sources_enabled(db)}


@router.get("/org-config")
def get_org_config(
    _: User = Depends(_require_administrator),
    db: Session = Depends(get_db),
):
    row = db.query(AppSetting).filter(AppSetting.key == ORG_CONFIG_KEY).first()
    if not row or not row.value.strip():
        return {"data": {}}
    try:
        return {"data": json.loads(row.value)}
    except json.JSONDecodeError:
        return {"data": {}}


@router.put("/org-config")
def put_org_config(
    body: OrgPortalConfigBody,
    _: User = Depends(_require_administrator),
    db: Session = Depends(get_db),
):
    raw = json.dumps(body.data, ensure_ascii=False)
    row = db.query(AppSetting).filter(AppSetting.key == ORG_CONFIG_KEY).first()
    if row:
        row.value = raw
    else:
        db.add(AppSetting(key=ORG_CONFIG_KEY, value=raw))
    db.commit()
    return {"ok": True}


@router.get("/team-overview")
def team_overview(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    if resolve_active_role(current_user, token) != PORTAL_CHIEF_EDITOR:
        raise HTTPException(status_code=403, detail="Нужна роль «Главный редактор»")
    rows = db.query(User).order_by(User.id).all()
    return [
        {
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "login": u.login,
            "portal_roles": portal_roles_for_user(u),
        }
        for u in rows
    ]


def _report_public(r: AnalysisReport) -> dict:
    return {
        "id": r.id,
        "filename": r.filename,
        "match_count": r.match_count,
        "status": r.status,
        "content_marking": getattr(r, "content_marking", None),
        "revision_done": bool(getattr(r, "revision_done", False)),
        "escalated": bool(getattr(r, "escalated", False)),
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@router.get("/lawyer/escalated-reports")
def lawyer_escalated_reports(
    _: User = Depends(_require_lawyer),
    db: Session = Depends(get_db),
):
    """US-L01: только эскалированные на юриста (флаг в БД)."""
    rows = (
        db.query(AnalysisReport)
        .filter(AnalysisReport.escalated.is_(True))
        .order_by(AnalysisReport.id.desc())
        .limit(200)
        .all()
    )
    return [_report_public(r) for r in rows]


@router.get("/metrics/summary")
def metrics_summary(
    period: str = Query("month", pattern="^(week|month|quarter|year)$"),
    _: User = Depends(_require_chief_editor),
    db: Session = Depends(get_db),
):
    """KPI, маркировка, статусы обработки, критические файлы — из analysis_reports и очереди."""
    cutoff = _period_cutoff(period)

    base = db.query(AnalysisReport).filter(AnalysisReport.created_at >= cutoff)

    reports_total = base.count()
    revisions_done = base.filter(AnalysisReport.revision_done.is_(True)).count()
    critical_count = base.filter(
        or_(AnalysisReport.content_marking == "banned", AnalysisReport.status == "error"),
    ).count()

    queue_active = (
        db.query(VideoAnalysisQueueItem)
        .filter(VideoAnalysisQueueItem.status.in_(("pending", "processing")))
        .count()
    )

    success_in_period = base.filter(AnalysisReport.status == "success")
    marking_counter: Counter[str] = Counter()
    for (m,) in success_in_period.with_entities(AnalysisReport.content_marking).all():
        key = m if m else "unclassified"
        marking_counter[key] += 1

    marking_buckets = []
    for key in ["clean", "age_12", "age_16", "age_18", "banned", "unclassified"]:
        c = marking_counter.get(key, 0)
        lbl, col = MARKING_LABELS[key]
        marking_buckets.append({"key": key, "label": lbl, "count": c, "color": col})

    proc_success = base.filter(AnalysisReport.status == "success").count()
    proc_processing = base.filter(AnalysisReport.status == "processing").count()
    proc_error = base.filter(AnalysisReport.status == "error").count()

    processing = [
        {"key": "success", "label": "Проверено (отчёт)", "count": proc_success, "color": "#2cd494"},
        {"key": "processing", "label": "В обработке", "count": proc_processing, "color": "#6898e8"},
        {"key": "error", "label": "Ошибка", "count": proc_error, "color": "#e45878"},
        {"key": "queue", "label": "В очереди API", "count": queue_active, "color": "#d4b838"},
    ]

    critical_rows = (
        base.filter(
            or_(AnalysisReport.content_marking == "banned", AnalysisReport.status == "error"),
        )
        .order_by(AnalysisReport.match_count.desc())
        .limit(25)
        .all()
    )

    editorial_rows = (
        db.query(AnalysisReport)
        .filter(
            AnalysisReport.status == "success",
            AnalysisReport.match_count > 0,
            AnalysisReport.revision_done.is_(False),
            AnalysisReport.escalated.is_(False),
        )
        .order_by(AnalysisReport.id.desc())
        .limit(30)
        .all()
    )

    return {
        "period": period,
        "period_days": PERIOD_DAYS.get(period, 30),
        "kpi": {
            "reports_total": reports_total,
            "queue_active": queue_active,
            "revisions_done": revisions_done,
            "critical": critical_count,
        },
        "marking": marking_buckets,
        "processing": processing,
        "critical_files": [_report_public(r) for r in critical_rows],
        "editorial_queue": [
            {
                **_report_public(r),
                "task": "Ревизия детекций" if (r.match_count or 0) > 0 else "",
            }
            for r in editorial_rows
        ],
    }


@router.get("/metrics/team")
def metrics_team(
    period: str = Query("month", pattern="^(week|month|quarter|year)$"),
    _: User = Depends(_require_chief_editor),
    db: Session = Depends(get_db),
):
    """Метрики по пользователям за период — агрегаты из analysis_reports."""
    cutoff = _period_cutoff(period)

    pending_case = case(
        (
            and_(
                AnalysisReport.status == "success",
                AnalysisReport.match_count > 0,
                AnalysisReport.revision_done.is_(False),
                AnalysisReport.escalated.is_(False),
            ),
            1,
        ),
        else_=0,
    )

    rows = (
        db.query(
            User.id,
            User.first_name,
            User.last_name,
            User.login,
            func.count(AnalysisReport.id).label("reports"),
            func.coalesce(func.sum(case((AnalysisReport.revision_done.is_(True), 1), else_=0)), 0).label(
                "verified"
            ),
            func.coalesce(func.sum(case((AnalysisReport.escalated.is_(True), 1), else_=0)), 0).label(
                "escalated"
            ),
            func.coalesce(func.sum(pending_case), 0).label("pending"),
        )
        .outerjoin(
            AnalysisReport,
            and_(AnalysisReport.created_by == User.id, AnalysisReport.created_at >= cutoff),
        )
        .group_by(User.id, User.first_name, User.last_name, User.login)
        .order_by(User.id)
        .all()
    )

    users_by_id = {u.id: u for u in db.query(User).order_by(User.id).all()}
    out = []
    for r in rows:
        rep = int(r.reports or 0)
        ver = int(r.verified or 0)
        esc = int(r.escalated or 0)
        pend = int(r.pending or 0)
        pct = round(ver * 100 / rep, 0) if rep > 0 else 0
        u = users_by_id.get(r.id)
        out.append(
            {
                "id": r.id,
                "first_name": r.first_name,
                "last_name": r.last_name,
                "login": r.login,
                "portal_roles": portal_roles_for_user(u) if u else [],
                "reports": rep,
                "verified": ver,
                "escalated": esc,
                "pending": pend,
                "productivity_pct": pct,
            }
        )
    return {"period": period, "members": out}
