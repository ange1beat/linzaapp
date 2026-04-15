"""Project CRUD, membership, sharing, and favorites routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.access_control import can_access_project, can_edit_project
from backend.auth import get_current_user
from backend.database import get_db
from backend.models import (
    Project, ProjectMember, ProjectShare, ReportShare,
    UserFavoriteProject, User,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ProjectCreate(BaseModel):
    name: str


class ProjectUpdate(BaseModel):
    name: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    tenant_id: int
    created_by: int | None = None
    avatar_url: str | None = None
    created_at: str | None = None
    is_favorite: bool = False

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int


class MemberAdd(BaseModel):
    user_ids: list[int]
    role: str = "viewer"


class MemberResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    email: str
    role: str


class MemberRoleUpdate(BaseModel):
    role: str  # "owner" | "editor" | "viewer"


class ShareCreate(BaseModel):
    share_type: str        # "user" | "team" | "tenant"
    share_target_id: int
    permission: str = "view"


class ShareResponse(BaseModel):
    id: int
    project_id: int
    share_type: str
    share_target_id: int
    permission: str
    shared_by: int | None = None

    class Config:
        from_attributes = True


class ReportShareCreate(BaseModel):
    user_ids: list[int]
    permission: str = "view"


class ReportShareResponse(BaseModel):
    id: int
    report_id: int
    user_id: int
    permission: str
    shared_by: int | None = None

    class Config:
        from_attributes = True


class MembershipResponse(BaseModel):
    user_id: int
    project_ids: list[int]


class MembershipUpdate(BaseModel):
    operation: str  # "add" | "remove"
    project_ids: list[int]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _project_response(p: Project, is_fav: bool = False) -> ProjectResponse:
    return ProjectResponse(
        id=p.id, name=p.name, tenant_id=p.tenant_id,
        created_by=p.created_by, avatar_url=p.avatar_url,
        created_at=str(p.created_at) if p.created_at else None,
        is_favorite=is_fav,
    )


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------


@router.get("/", response_model=ProjectListResponse)
def list_projects(
    name: str = "",
    PageSize: int = Query(10, alias="PageSize", ge=1, le=100),
    PageNumber: int = Query(1, alias="PageNumber", ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List projects visible to the current user (owned + member + shared + same tenant)."""
    # Base: projects in the same tenant + projects shared directly
    member_project_ids = [
        pm.project_id
        for pm in db.query(ProjectMember.project_id).filter(ProjectMember.user_id == current_user.id).all()
    ]
    share_project_ids = [
        ps.project_id
        for ps in db.query(ProjectShare.project_id).filter(
            ProjectShare.share_type == "user",
            ProjectShare.share_target_id == current_user.id,
        ).all()
    ]
    team_share_ids = []
    if current_user.team_id:
        team_share_ids = [
            ps.project_id
            for ps in db.query(ProjectShare.project_id).filter(
                ProjectShare.share_type == "team",
                ProjectShare.share_target_id == current_user.team_id,
            ).all()
        ]

    visible_ids = set(member_project_ids + share_project_ids + team_share_ids)

    q = db.query(Project)
    if current_user.role == "superadmin":
        pass  # see all
    elif current_user.tenant_id:
        q = q.filter(
            or_(
                Project.tenant_id == current_user.tenant_id,
                Project.id.in_(visible_ids) if visible_ids else False,
            )
        )
    else:
        q = q.filter(
            or_(
                Project.created_by == current_user.id,
                Project.id.in_(visible_ids) if visible_ids else False,
            )
        )

    if name:
        q = q.filter(Project.name.ilike(f"%{name}%"))

    total = q.count()
    offset = (PageNumber - 1) * PageSize
    projects = q.order_by(Project.created_at.desc()).offset(offset).limit(PageSize).all()

    # Check favorites
    fav_ids = set(
        f.project_id
        for f in db.query(UserFavoriteProject.project_id).filter(
            UserFavoriteProject.user_id == current_user.id
        ).all()
    )

    return ProjectListResponse(
        projects=[_project_response(p, p.id in fav_ids) for p in projects],
        total=total,
    )


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    body: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.tenant_id:
        raise HTTPException(status_code=400, detail="Пользователь не принадлежит тенанту")

    project = Project(
        name=body.name.strip(),
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
    )
    db.add(project)
    db.flush()

    # Creator is automatically an owner member
    member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(member)
    db.commit()
    db.refresh(project)
    return _project_response(project)


@router.get("/favorites", response_model=list[ProjectResponse])
def list_favorite_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favs = db.query(UserFavoriteProject).filter(
        UserFavoriteProject.user_id == current_user.id,
    ).all()
    project_ids = [f.project_id for f in favs]
    if not project_ids:
        return []
    projects = db.query(Project).filter(Project.id.in_(project_ids)).all()
    return [_project_response(p, is_fav=True) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_access_project(current_user, project_id, db):
        raise HTTPException(status_code=403, detail="Нет доступа к проекту")
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    is_fav = db.query(UserFavoriteProject).filter(
        UserFavoriteProject.user_id == current_user.id,
        UserFavoriteProject.project_id == project_id,
    ).first() is not None

    return _project_response(project, is_fav)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    body: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_edit_project(current_user, project_id, db):
        raise HTTPException(status_code=403, detail="Нет прав на редактирование")
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    if body.name is not None:
        project.name = body.name.strip()
    db.commit()
    db.refresh(project)
    return _project_response(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    if project.created_by != current_user.id and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Только владелец может удалить проект")

    db.query(ProjectMember).filter(ProjectMember.project_id == project_id).delete()
    db.query(ProjectShare).filter(ProjectShare.project_id == project_id).delete()
    db.query(UserFavoriteProject).filter(UserFavoriteProject.project_id == project_id).delete()
    db.delete(project)
    db.commit()


@router.post("/{project_id}/favorite")
def toggle_favorite(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fav = db.query(UserFavoriteProject).filter(
        UserFavoriteProject.user_id == current_user.id,
        UserFavoriteProject.project_id == project_id,
    ).first()
    if fav:
        db.delete(fav)
        db.commit()
        return {"is_favorite": False}
    else:
        db.add(UserFavoriteProject(user_id=current_user.id, project_id=project_id))
        db.commit()
        return {"is_favorite": True}


# ---------------------------------------------------------------------------
# Project members
# ---------------------------------------------------------------------------


@router.get("/{project_id}/members", response_model=list[MemberResponse])
def list_project_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_access_project(current_user, project_id, db):
        raise HTTPException(status_code=403, detail="Нет доступа")

    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    result = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            result.append(MemberResponse(
                id=m.id, user_id=user.id, first_name=user.first_name,
                last_name=user.last_name, email=user.email, role=m.role,
            ))
    return result


@router.post("/{project_id}/members", status_code=200)
def add_project_members(
    project_id: int,
    body: MemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_edit_project(current_user, project_id, db):
        raise HTTPException(status_code=403, detail="Нет прав")

    added = 0
    for uid in body.user_ids:
        existing = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == uid,
        ).first()
        if not existing:
            db.add(ProjectMember(project_id=project_id, user_id=uid, role=body.role))
            added += 1
    db.commit()
    return {"added": added}


@router.delete("/{project_id}/members/{user_id}", status_code=204)
def remove_project_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_edit_project(current_user, project_id, db):
        raise HTTPException(status_code=403, detail="Нет прав")

    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Участник не найден")
    db.delete(member)
    db.commit()


@router.patch("/{project_id}/members/{user_id}", response_model=MemberResponse)
def update_member_role(
    project_id: int,
    user_id: int,
    body: MemberRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.role not in ("owner", "editor", "viewer"):
        raise HTTPException(status_code=400, detail="Роль должна быть owner, editor или viewer")
    if not can_edit_project(current_user, project_id, db):
        raise HTTPException(status_code=403, detail="Нет прав")

    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Участник не найден")
    member.role = body.role
    db.commit()

    user = db.query(User).filter(User.id == user_id).first()
    return MemberResponse(
        id=member.id, user_id=user.id, first_name=user.first_name,
        last_name=user.last_name, email=user.email, role=member.role,
    )


# ---------------------------------------------------------------------------
# Project sharing
# ---------------------------------------------------------------------------


@router.post("/{project_id}/share", response_model=ShareResponse, status_code=201)
def share_project(
    project_id: int,
    body: ShareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_edit_project(current_user, project_id, db):
        raise HTTPException(status_code=403, detail="Нет прав")
    if body.share_type not in ("user", "team", "tenant"):
        raise HTTPException(status_code=400, detail="share_type должен быть user, team или tenant")

    existing = db.query(ProjectShare).filter(
        ProjectShare.project_id == project_id,
        ProjectShare.share_type == body.share_type,
        ProjectShare.share_target_id == body.share_target_id,
    ).first()
    if existing:
        existing.permission = body.permission
        db.commit()
        db.refresh(existing)
        return ShareResponse(
            id=existing.id, project_id=existing.project_id,
            share_type=existing.share_type, share_target_id=existing.share_target_id,
            permission=existing.permission, shared_by=existing.shared_by,
        )

    share = ProjectShare(
        project_id=project_id,
        share_type=body.share_type,
        share_target_id=body.share_target_id,
        permission=body.permission,
        shared_by=current_user.id,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return ShareResponse(
        id=share.id, project_id=share.project_id,
        share_type=share.share_type, share_target_id=share.share_target_id,
        permission=share.permission, shared_by=share.shared_by,
    )


@router.get("/{project_id}/shares", response_model=list[ShareResponse])
def list_project_shares(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_access_project(current_user, project_id, db):
        raise HTTPException(status_code=403, detail="Нет доступа")
    shares = db.query(ProjectShare).filter(ProjectShare.project_id == project_id).all()
    return [
        ShareResponse(
            id=s.id, project_id=s.project_id,
            share_type=s.share_type, share_target_id=s.share_target_id,
            permission=s.permission, shared_by=s.shared_by,
        )
        for s in shares
    ]


@router.delete("/{project_id}/share/{share_id}", status_code=204)
def revoke_project_share(
    project_id: int,
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_edit_project(current_user, project_id, db):
        raise HTTPException(status_code=403, detail="Нет прав")
    share = db.query(ProjectShare).filter(
        ProjectShare.id == share_id,
        ProjectShare.project_id == project_id,
    ).first()
    if not share:
        raise HTTPException(status_code=404, detail="Шеринг не найден")
    db.delete(share)
    db.commit()


# ---------------------------------------------------------------------------
# Membership shortcuts (linza-admin compatibility)
# ---------------------------------------------------------------------------


@router.get("/membership/{user_id}", response_model=MembershipResponse)
def get_user_membership(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    members = db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()
    return MembershipResponse(
        user_id=user_id,
        project_ids=[m.project_id for m in members],
    )


@router.patch("/membership/{user_id}", response_model=MembershipResponse)
def update_user_membership(
    user_id: int,
    body: MembershipUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.operation == "add":
        for pid in body.project_ids:
            existing = db.query(ProjectMember).filter(
                ProjectMember.project_id == pid,
                ProjectMember.user_id == user_id,
            ).first()
            if not existing:
                db.add(ProjectMember(project_id=pid, user_id=user_id, role="viewer"))
    elif body.operation == "remove":
        db.query(ProjectMember).filter(
            ProjectMember.user_id == user_id,
            ProjectMember.project_id.in_(body.project_ids),
        ).delete(synchronize_session=False)

    db.commit()
    members = db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()
    return MembershipResponse(
        user_id=user_id,
        project_ids=[m.project_id for m in members],
    )


# ---------------------------------------------------------------------------
# Report sharing (extends analysis_reports)
# ---------------------------------------------------------------------------


@router.post("/reports/{report_id}/share", response_model=list[ReportShareResponse], status_code=201)
def share_report(
    report_id: int,
    body: ReportShareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from backend.models import AnalysisReport
    report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Отчёт не найден")
    if report.created_by != current_user.id and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Только владелец может делиться отчётом")

    created = []
    for uid in body.user_ids:
        existing = db.query(ReportShare).filter(
            ReportShare.report_id == report_id,
            ReportShare.user_id == uid,
        ).first()
        if existing:
            existing.permission = body.permission
            created.append(existing)
        else:
            rs = ReportShare(
                report_id=report_id,
                user_id=uid,
                permission=body.permission,
                shared_by=current_user.id,
            )
            db.add(rs)
            created.append(rs)
    db.commit()

    return [
        ReportShareResponse(
            id=rs.id, report_id=rs.report_id, user_id=rs.user_id,
            permission=rs.permission, shared_by=rs.shared_by,
        )
        for rs in created
    ]


@router.get("/reports/{report_id}/shares", response_model=list[ReportShareResponse])
def list_report_shares(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from backend.access_control import can_access_report
    if not can_access_report(current_user, report_id, db):
        raise HTTPException(status_code=403, detail="Нет доступа")
    shares = db.query(ReportShare).filter(ReportShare.report_id == report_id).all()
    return [
        ReportShareResponse(
            id=s.id, report_id=s.report_id, user_id=s.user_id,
            permission=s.permission, shared_by=s.shared_by,
        )
        for s in shares
    ]


@router.delete("/reports/{report_id}/share/{share_id}", status_code=204)
def revoke_report_share(
    report_id: int,
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    share = db.query(ReportShare).filter(
        ReportShare.id == share_id,
        ReportShare.report_id == report_id,
    ).first()
    if not share:
        raise HTTPException(status_code=404, detail="Шеринг не найден")
    if share.shared_by != current_user.id and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Нет прав")
    db.delete(share)
    db.commit()
