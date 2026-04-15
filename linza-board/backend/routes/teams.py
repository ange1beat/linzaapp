"""Team CRUD and membership routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import get_current_user, require_manager
from backend.database import get_db
from backend.models import Team, User

router = APIRouter()


class TeamCreate(BaseModel):
    name: str


class TeamUpdate(BaseModel):
    name: str | None = None


class TeamMemberAdd(BaseModel):
    user_ids: list[int]


class TeamMemberResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    id: int
    name: str
    tenant_id: int
    member_count: int = 0
    created_at: str | None = None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[TeamResponse])
def list_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List teams within the current user's tenant."""
    if not current_user.tenant_id:
        return []
    teams = db.query(Team).filter(Team.tenant_id == current_user.tenant_id).order_by(Team.id).all()
    result = []
    for t in teams:
        count = db.query(User).filter(User.team_id == t.id).count()
        result.append(TeamResponse(
            id=t.id, name=t.name, tenant_id=t.tenant_id, member_count=count,
            created_at=str(t.created_at) if t.created_at else None,
        ))
    return result


@router.post("/", response_model=TeamResponse, status_code=201)
def create_team(
    body: TeamCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    if not current_user.tenant_id:
        raise HTTPException(status_code=400, detail="Пользователь не принадлежит тенанту")

    team = Team(
        name=body.name.strip(),
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return TeamResponse(
        id=team.id, name=team.name, tenant_id=team.tenant_id, member_count=0,
        created_at=str(team.created_at) if team.created_at else None,
    )


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    if team.tenant_id != current_user.tenant_id and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Нет доступа к этой команде")

    count = db.query(User).filter(User.team_id == team.id).count()
    return TeamResponse(
        id=team.id, name=team.name, tenant_id=team.tenant_id, member_count=count,
        created_at=str(team.created_at) if team.created_at else None,
    )


@router.patch("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    body: TeamUpdate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    if team.tenant_id != current_user.tenant_id and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Нет доступа")

    if body.name is not None:
        team.name = body.name.strip()
    db.commit()
    db.refresh(team)

    count = db.query(User).filter(User.team_id == team.id).count()
    return TeamResponse(
        id=team.id, name=team.name, tenant_id=team.tenant_id, member_count=count,
        created_at=str(team.created_at) if team.created_at else None,
    )


@router.delete("/{team_id}", status_code=204)
def delete_team(
    team_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    if team.tenant_id != current_user.tenant_id and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Нет доступа")

    # Unassign users from this team
    db.query(User).filter(User.team_id == team_id).update({"team_id": None})
    db.delete(team)
    db.commit()


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse])
def list_team_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    members = db.query(User).filter(User.team_id == team_id).all()
    return [
        TeamMemberResponse(id=u.id, first_name=u.first_name, last_name=u.last_name, email=u.email, role=u.role)
        for u in members
    ]


@router.post("/{team_id}/members", status_code=200)
def add_team_members(
    team_id: int,
    body: TeamMemberAdd,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    updated = 0
    for uid in body.user_ids:
        user = db.query(User).filter(User.id == uid).first()
        if user and user.tenant_id == team.tenant_id:
            user.team_id = team_id
            updated += 1
    db.commit()
    return {"updated": updated}


@router.delete("/{team_id}/members/{user_id}", status_code=204)
def remove_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id, User.team_id == team_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден в команде")
    user.team_id = None
    db.commit()
