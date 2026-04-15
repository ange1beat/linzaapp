"""Storage quota management routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import get_current_user, require_manager
from backend.database import get_db
from backend.models import StorageQuota, Team, User

router = APIRouter()

VALID_SCOPE_TYPES = ("tenant", "team", "user")


class QuotaCreate(BaseModel):
    scope_type: str    # "tenant" | "team" | "user"
    scope_id: int
    quota_bytes: int


class QuotaUpdate(BaseModel):
    quota_bytes: int


class QuotaResponse(BaseModel):
    id: int
    scope_type: str
    scope_id: int
    quota_bytes: int
    used_bytes: int

    class Config:
        from_attributes = True


class StorageUsageResponse(BaseModel):
    user: QuotaResponse | None = None
    team: QuotaResponse | None = None
    tenant: QuotaResponse | None = None


@router.get("/quotas", response_model=list[QuotaResponse])
def list_quotas(
    scope_type: str | None = None,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    q = db.query(StorageQuota)
    if scope_type:
        q = q.filter(StorageQuota.scope_type == scope_type)
    quotas = q.order_by(StorageQuota.id).all()
    return [
        QuotaResponse(
            id=sq.id, scope_type=sq.scope_type, scope_id=sq.scope_id,
            quota_bytes=sq.quota_bytes, used_bytes=sq.used_bytes or 0,
        )
        for sq in quotas
    ]


@router.post("/quotas", response_model=QuotaResponse, status_code=201)
def create_quota(
    body: QuotaCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    if body.scope_type not in VALID_SCOPE_TYPES:
        raise HTTPException(status_code=400, detail=f"scope_type должен быть одним из: {VALID_SCOPE_TYPES}")

    existing = db.query(StorageQuota).filter(
        StorageQuota.scope_type == body.scope_type,
        StorageQuota.scope_id == body.scope_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Квота для данного scope уже существует")

    quota = StorageQuota(
        scope_type=body.scope_type,
        scope_id=body.scope_id,
        quota_bytes=body.quota_bytes,
    )
    db.add(quota)
    db.commit()
    db.refresh(quota)
    return QuotaResponse(
        id=quota.id, scope_type=quota.scope_type, scope_id=quota.scope_id,
        quota_bytes=quota.quota_bytes, used_bytes=quota.used_bytes or 0,
    )


@router.get("/quotas/{scope_type}/{scope_id}", response_model=QuotaResponse)
def get_quota(
    scope_type: str,
    scope_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quota = db.query(StorageQuota).filter(
        StorageQuota.scope_type == scope_type,
        StorageQuota.scope_id == scope_id,
    ).first()
    if not quota:
        raise HTTPException(status_code=404, detail="Квота не найдена")
    return QuotaResponse(
        id=quota.id, scope_type=quota.scope_type, scope_id=quota.scope_id,
        quota_bytes=quota.quota_bytes, used_bytes=quota.used_bytes or 0,
    )


@router.put("/quotas/{scope_type}/{scope_id}", response_model=QuotaResponse)
def update_quota(
    scope_type: str,
    scope_id: int,
    body: QuotaUpdate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    quota = db.query(StorageQuota).filter(
        StorageQuota.scope_type == scope_type,
        StorageQuota.scope_id == scope_id,
    ).first()
    if not quota:
        raise HTTPException(status_code=404, detail="Квота не найдена")
    quota.quota_bytes = body.quota_bytes
    db.commit()
    db.refresh(quota)
    return QuotaResponse(
        id=quota.id, scope_type=quota.scope_type, scope_id=quota.scope_id,
        quota_bytes=quota.quota_bytes, used_bytes=quota.used_bytes or 0,
    )


@router.delete("/quotas/{scope_type}/{scope_id}", status_code=204)
def delete_quota(
    scope_type: str,
    scope_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    quota = db.query(StorageQuota).filter(
        StorageQuota.scope_type == scope_type,
        StorageQuota.scope_id == scope_id,
    ).first()
    if not quota:
        raise HTTPException(status_code=404, detail="Квота не найдена")
    db.delete(quota)
    db.commit()


@router.get("/usage", response_model=StorageUsageResponse)
def get_storage_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get hierarchical storage usage for the current user (user/team/tenant)."""

    def _quota_resp(sq: StorageQuota | None) -> QuotaResponse | None:
        if not sq:
            return None
        return QuotaResponse(
            id=sq.id, scope_type=sq.scope_type, scope_id=sq.scope_id,
            quota_bytes=sq.quota_bytes, used_bytes=sq.used_bytes or 0,
        )

    user_quota = db.query(StorageQuota).filter(
        StorageQuota.scope_type == "user",
        StorageQuota.scope_id == current_user.id,
    ).first()

    team_quota = None
    if current_user.team_id:
        team_quota = db.query(StorageQuota).filter(
            StorageQuota.scope_type == "team",
            StorageQuota.scope_id == current_user.team_id,
        ).first()

    tenant_quota = None
    if current_user.tenant_id:
        tenant_quota = db.query(StorageQuota).filter(
            StorageQuota.scope_type == "tenant",
            StorageQuota.scope_id == current_user.tenant_id,
        ).first()

    return StorageUsageResponse(
        user=_quota_resp(user_quota),
        team=_quota_resp(team_quota),
        tenant=_quota_resp(tenant_quota),
    )
