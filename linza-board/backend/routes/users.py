import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.auth import (
    PORTAL_ADMINISTRATOR,
    get_current_user,
    hash_password,
    oauth2_scheme,
    portal_roles_for_user,
    require_manager,
    resolve_active_role,
    verify_password,
    VALID_PORTAL_ROLES,
)
from backend.database import get_db
from backend.models import User

router = APIRouter()


class CreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    login: str
    password: str
    email: str
    role: str  # "admin" or "user"
    portal_roles: list[str] | None = None  # роли портала PRD; None = вычислять из legacy role


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    login: str
    email: str
    role: str
    portal_roles: list[str]
    created_by: int | None


class UpdateUserRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    role: str | None = None
    password: str | None = None
    portal_roles: list[str] | None = None


def _user_to_response(u: User) -> UserResponse:
    return UserResponse(
        id=u.id,
        first_name=u.first_name,
        last_name=u.last_name,
        login=u.login,
        email=u.email,
        role=u.role,
        portal_roles=portal_roles_for_user(u),
        created_by=u.created_by,
    )


def _portal_roles_json(raw: list[str] | None) -> str | None:
    if raw is None:
        return None
    cleaned = [x for x in raw if x in VALID_PORTAL_ROLES]
    if not cleaned:
        return None
    return json.dumps(cleaned)


def _is_org_admin(current_user: User, token: str) -> bool:
    if current_user.role == "superadmin":
        return True
    return resolve_active_role(current_user, token) == PORTAL_ADMINISTRATOR


@router.get("/", response_model=list[UserResponse])
def list_users(
    current_user: User = Depends(require_manager),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    if current_user.role == "superadmin" or _is_org_admin(current_user, token):
        rows = db.query(User).order_by(User.id).all()
    else:
        rows = (
            db.query(User)
            .filter(User.created_by == current_user.id)
            .order_by(User.id)
            .all()
        )
    return [_user_to_response(u) for u in rows]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    req: CreateUserRequest,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    if req.role not in ("admin", "user"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Роль должна быть 'admin' или 'user'",
        )

    if req.role == "admin" and current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только суперадмин может создавать администраторов",
        )

    if db.query(User).filter(User.login == req.login).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким логином уже существует",
        )

    pr_json = _portal_roles_json(req.portal_roles)
    user = User(
        first_name=req.first_name,
        last_name=req.last_name,
        login=req.login,
        password_hash=hash_password(req.password),
        email=req.email,
        role=req.role,
        portal_roles=pr_json,
        created_by=current_user.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_to_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    req: UpdateUserRequest,
    current_user: User = Depends(require_manager),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    if user.role == "superadmin" and current_user.role != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на редактирование суперадмина")

    org_admin = _is_org_admin(current_user, token)
    if not org_admin and current_user.role == "admin":
        if user.created_by != current_user.id and user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на редактирование этого пользователя")

    if req.role is not None:
        if req.role not in ("admin", "user"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Роль должна быть 'admin' или 'user'")
        if req.role == "admin" and current_user.role != "superadmin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только суперадмин может назначать роль администратора")
        if user.role == "superadmin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нельзя изменить роль суперадмина")
        user.role = req.role

    if req.first_name is not None:
        user.first_name = req.first_name
    if req.last_name is not None:
        user.last_name = req.last_name
    if req.email is not None:
        user.email = req.email
    if req.password is not None:
        if len(req.password) < 4:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пароль должен быть не менее 4 символов")
        user.password_hash = hash_password(req.password)
    if req.portal_roles is not None:
        user.portal_roles = _portal_roles_json(req.portal_roles)

    db.commit()
    db.refresh(user)
    return _user_to_response(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_manager),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    if user.role == "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нельзя удалить суперадмина")

    org_admin = _is_org_admin(current_user, token)
    if not org_admin and current_user.role == "admin" and user.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на удаление этого пользователя")

    db.delete(user)
    db.commit()


# ---------------------------------------------------------------------------
# Extended endpoints for linza-admin compatibility
# ---------------------------------------------------------------------------


class UserSearchRequest(BaseModel):
    searchTerm: str | None = None
    pageNumber: int = 1
    pageSize: int = 10
    includeIds: list[str] | None = None
    excludeIds: list[str] | None = None


class FullUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    login: str
    email: str
    role: str
    portal_roles: list[str]
    phone_number: str | None = None
    telegram_username: str | None = None
    avatar_url: str | None = None
    tenant_id: int | None = None
    team_id: int | None = None
    last_login_at: str | None = None
    created_by: int | None = None


class UsersSearchResponse(BaseModel):
    users: list[FullUserResponse]
    total: int


def _full_user_response(u: User) -> FullUserResponse:
    return FullUserResponse(
        id=u.id,
        first_name=u.first_name,
        last_name=u.last_name,
        login=u.login,
        email=u.email,
        role=u.role,
        portal_roles=portal_roles_for_user(u),
        phone_number=u.phone_number,
        telegram_username=u.telegram_username,
        avatar_url=u.avatar_url,
        tenant_id=u.tenant_id,
        team_id=u.team_id,
        last_login_at=str(u.last_login_at) if u.last_login_at else None,
        created_by=u.created_by,
    )


@router.post("/search", response_model=UsersSearchResponse)
def search_users(
    body: UserSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search members with pagination, filtering, include/exclude IDs."""
    q = db.query(User)

    # Tenant scope
    if current_user.tenant_id and current_user.role != "superadmin":
        q = q.filter(User.tenant_id == current_user.tenant_id)

    # Search term
    if body.searchTerm:
        term = f"%{body.searchTerm}%"
        q = q.filter(
            or_(
                User.first_name.ilike(term),
                User.last_name.ilike(term),
                User.email.ilike(term),
                User.login.ilike(term),
            )
        )

    # Exclude IDs
    if body.excludeIds:
        exclude_int = [int(x) for x in body.excludeIds if x.isdigit()]
        if exclude_int:
            q = q.filter(~User.id.in_(exclude_int))

    total = q.count()

    # Pagination
    offset = (body.pageNumber - 1) * body.pageSize
    users = q.order_by(User.id).offset(offset).limit(body.pageSize).all()

    # Include IDs (force-include users even if filtered out)
    result = [_full_user_response(u) for u in users]
    if body.includeIds:
        include_int = [int(x) for x in body.includeIds if x.isdigit()]
        existing_ids = {u.id for u in users}
        for uid in include_int:
            if uid not in existing_ids:
                inc_user = db.query(User).filter(User.id == uid).first()
                if inc_user:
                    result.append(_full_user_response(inc_user))

    return UsersSearchResponse(users=result, total=total)


@router.get("/me", response_model=FullUserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user's full profile."""
    return _full_user_response(current_user)


@router.get("/{user_id}", response_model=FullUserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user by ID with full profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return _full_user_response(user)


class UpdateNameRequest(BaseModel):
    firstName: str
    lastName: str


class UpdatePasswordRequest(BaseModel):
    currentPassword: str
    newPassword: str


class UpdateTelegramRequest(BaseModel):
    username: str


@router.put("/me/name", response_model=FullUserResponse)
def update_my_name(
    body: UpdateNameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.first_name = body.firstName.strip()
    current_user.last_name = body.lastName.strip()
    db.commit()
    db.refresh(current_user)
    return _full_user_response(current_user)


@router.put("/me/password")
def update_my_password(
    body: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.currentPassword, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")
    if len(body.newPassword) < 8:
        raise HTTPException(status_code=400, detail="Пароль должен быть не менее 8 символов")
    current_user.password_hash = hash_password(body.newPassword)
    db.commit()
    return {"detail": "Пароль успешно изменён"}


@router.put("/me/telegram", response_model=FullUserResponse)
def update_my_telegram(
    body: UpdateTelegramRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.telegram_username = body.username.lstrip("@").strip()
    db.commit()
    db.refresh(current_user)
    return _full_user_response(current_user)


@router.put("/me/avatar", response_model=FullUserResponse)
async def update_my_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Store avatar as data URL for simplicity; in production use S3
    content = await file.read()
    import base64
    data_url = f"data:{file.content_type};base64,{base64.b64encode(content).decode()}"
    current_user.avatar_url = data_url
    db.commit()
    db.refresh(current_user)
    return _full_user_response(current_user)


@router.patch("/{user_id}/roles")
def update_user_roles(
    user_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
    isSupervisor: bool = False,
):
    """Toggle User/Supervisor role (linza-admin compatibility)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if isSupervisor:
        user.portal_roles = json.dumps(["administrator", "operator"])
    else:
        user.portal_roles = json.dumps(["operator"])
    db.commit()
    return {"id": user.id, "roles": ["Supervisor"] if isSupervisor else ["User"]}
