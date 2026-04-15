import json
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Tenant, User

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "linza-board-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("AUTH_TOKEN_EXPIRE_MINUTES", "480"))  # 8 hours

# Superadmin seed credentials (env vars)
ADMIN_LOGIN = os.getenv("AUTH_ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("AUTH_ADMIN_PASSWORD", "admin")
ADMIN_EMAIL = os.getenv("AUTH_ADMIN_EMAIL", "admin@linza.local")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

# Роли портала Linza Detector (PRD, подход B — переключение контекста)
PORTAL_ADMINISTRATOR = "administrator"
PORTAL_OPERATOR = "operator"
PORTAL_LAWYER = "lawyer"
PORTAL_CHIEF_EDITOR = "chief_editor"
VALID_PORTAL_ROLES = frozenset({
    PORTAL_ADMINISTRATOR,
    PORTAL_OPERATOR,
    PORTAL_LAWYER,
    PORTAL_CHIEF_EDITOR,
})


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)


def check_credentials(db: Session, login: str, password: str) -> User | None:
    user = db.query(User).filter(User.login == login).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def portal_roles_for_user(user: User) -> list[str]:
    """Список ролей портала: из БД (JSON) или по legacy-роли."""
    raw = getattr(user, "portal_roles", None)
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                out = [str(x) for x in parsed if str(x) in VALID_PORTAL_ROLES]
                if out:
                    return out
        except (json.JSONDecodeError, TypeError):
            pass
    if user.role == "superadmin":
        return [
            PORTAL_ADMINISTRATOR,
            PORTAL_OPERATOR,
            PORTAL_LAWYER,
            PORTAL_CHIEF_EDITOR,
        ]
    if user.role == "admin":
        return [PORTAL_ADMINISTRATOR, PORTAL_OPERATOR]
    return [PORTAL_OPERATOR]


def pick_default_active_role(roles: list[str]) -> str | None:
    if not roles:
        return None
    if PORTAL_OPERATOR in roles:
        return PORTAL_OPERATOR
    return roles[0]


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def resolve_active_role(user: User, token: str | None) -> str | None:
    pr = portal_roles_for_user(user)
    if not pr:
        return None
    if not token:
        return pr[0]
    try:
        payload = decode_access_token(token)
    except JWTError:
        return pr[0]
    ar = payload.get("ar")
    if isinstance(ar, str) and ar in pr:
        return ar
    return pr[0]


def build_token_payload(user: User) -> dict:
    """Build JWT payload with portal roles and tenant/team context."""
    pr = portal_roles_for_user(user)
    ar = pick_default_active_role(pr)
    return {
        "sub": user.login,
        "role": user.role,
        "pr": pr,
        "ar": ar,
        "tid": user.tenant_id,
        "gid": user.team_id,
    }


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if not login:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.login == login).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_manager(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Управление пользователями: legacy admin/superadmin или активная роль administrator."""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if current_user.role in ("superadmin", "admin"):
        return current_user
    if resolve_active_role(current_user, token) == PORTAL_ADMINISTRATOR:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав для управления пользователями",
    )


def require_portal_role(*allowed_roles: str):
    """Factory: returns a dependency that checks if user has one of the allowed portal roles."""
    def checker(
        current_user: User = Depends(get_current_user),
        token: str = Depends(oauth2_scheme),
    ) -> User:
        if current_user.role == "superadmin":
            return current_user
        ar = resolve_active_role(current_user, token)
        if ar in allowed_roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Требуется одна из ролей: {', '.join(allowed_roles)}",
        )
    return checker


def _ensure_default_tenant(db: Session) -> int:
    """Ensure the default tenant exists and return its id."""
    tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
    if not tenant:
        tenant = Tenant(name="Default Organization", slug="default")
        db.add(tenant)
        db.flush()
    return tenant.id


def seed_superadmin(db: Session):
    """Create superadmin user if not exists. Ensures default tenant."""
    tenant_id = _ensure_default_tenant(db)

    existing = db.query(User).filter(User.login == ADMIN_LOGIN).first()
    if not existing:
        superadmin = User(
            first_name="Super",
            last_name="Admin",
            login=ADMIN_LOGIN,
            password_hash=hash_password(ADMIN_PASSWORD),
            email=ADMIN_EMAIL,
            role="superadmin",
            created_by=None,
            tenant_id=tenant_id,
        )
        db.add(superadmin)
    elif existing.tenant_id is None:
        existing.tenant_id = tenant_id

    db.commit()
