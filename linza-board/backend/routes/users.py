import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import (
    PORTAL_ADMINISTRATOR,
    hash_password,
    oauth2_scheme,
    portal_roles_for_user,
    require_manager,
    resolve_active_role,
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
