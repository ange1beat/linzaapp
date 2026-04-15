"""Access control helpers for projects and reports."""

from sqlalchemy.orm import Session

from backend.models import Project, ProjectMember, ProjectShare, ReportShare, User


def can_access_project(user: User, project_id: int, db: Session) -> bool:
    """Check if user can view a project (owner, member, team share, or tenant share)."""
    if user.role == "superadmin":
        return True

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False

    # Owner
    if project.created_by == user.id:
        return True

    # Direct member
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id,
    ).first()
    if member:
        return True

    # Shared with user directly
    share = db.query(ProjectShare).filter(
        ProjectShare.project_id == project_id,
        ProjectShare.share_type == "user",
        ProjectShare.share_target_id == user.id,
    ).first()
    if share:
        return True

    # Shared with user's team
    if user.team_id:
        team_share = db.query(ProjectShare).filter(
            ProjectShare.project_id == project_id,
            ProjectShare.share_type == "team",
            ProjectShare.share_target_id == user.team_id,
        ).first()
        if team_share:
            return True

    # Shared with user's tenant
    if user.tenant_id:
        tenant_share = db.query(ProjectShare).filter(
            ProjectShare.project_id == project_id,
            ProjectShare.share_type == "tenant",
            ProjectShare.share_target_id == user.tenant_id,
        ).first()
        if tenant_share:
            return True

    # Same tenant
    if user.tenant_id and project.tenant_id == user.tenant_id:
        return True

    return False


def can_edit_project(user: User, project_id: int, db: Session) -> bool:
    """Check if user can edit a project (owner, member with editor+, or shared with edit permission)."""
    if user.role == "superadmin":
        return True

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False

    if project.created_by == user.id:
        return True

    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id,
    ).first()
    if member and member.role in ("owner", "editor"):
        return True

    share = db.query(ProjectShare).filter(
        ProjectShare.project_id == project_id,
        ProjectShare.share_type == "user",
        ProjectShare.share_target_id == user.id,
        ProjectShare.permission == "edit",
    ).first()
    if share:
        return True

    return False


def can_access_report(user: User, report_id: int, db: Session) -> bool:
    """Check if user can view a report (owner or shared)."""
    if user.role == "superadmin":
        return True

    from backend.models import AnalysisReport
    report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
    if not report:
        return False

    if report.created_by == user.id:
        return True

    share = db.query(ReportShare).filter(
        ReportShare.report_id == report_id,
        ReportShare.user_id == user.id,
    ).first()
    if share:
        return True

    return False
