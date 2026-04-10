from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.requests import Request

from backend.auth import (
    check_credentials,
    create_access_token,
    get_current_user,
    oauth2_scheme,
    pick_default_active_role,
    portal_roles_for_user,
    resolve_active_role,
    VALID_PORTAL_ROLES,
)
from backend.database import get_db
from backend.models import User
from backend.rate_limit import limiter

router = APIRouter()


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SwitchRoleRequest(BaseModel):
    active_role: str


class MeResponse(BaseModel):
    login: str
    role: str
    first_name: str
    last_name: str
    email: str
    portal_roles: list[str]
    active_role: str | None


def _issue_token(user: User, active_role: str | None = None) -> str:
    pr = portal_roles_for_user(user)
    ar = active_role if (active_role and active_role in pr) else pick_default_active_role(pr)
    return create_access_token(
        {
            "sub": user.login,
            "role": user.role,
            "pr": pr,
            "ar": ar,
        }
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, req: LoginRequest, db: Session = Depends(get_db)):
    user = check_credentials(db, req.login, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    return TokenResponse(access_token=_issue_token(user))


@router.post("/switch-role", response_model=TokenResponse)
def switch_role(
    body: SwitchRoleRequest,
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    if body.active_role not in VALID_PORTAL_ROLES:
        raise HTTPException(status_code=400, detail="Неизвестная роль портала")
    pr = portal_roles_for_user(current_user)
    if body.active_role not in pr:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Эта роль не назначена пользователю",
        )
    return TokenResponse(access_token=_issue_token(current_user, body.active_role))


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    pr = portal_roles_for_user(current_user)
    ar = resolve_active_role(current_user, token)
    return MeResponse(
        login=current_user.login,
        role=current_user.role,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        portal_roles=pr,
        active_role=ar,
    )
