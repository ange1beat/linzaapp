"""Tenant CRUD routes."""

import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import get_current_user, require_manager
from backend.database import get_db
from backend.models import Tenant, User

router = APIRouter()


class TenantCreate(BaseModel):
    name: str
    slug: str | None = None


class TenantUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None


class TenantResponse(BaseModel):
    id: int
    name: str
    slug: str
    created_at: str | None = None

    class Config:
        from_attributes = True


def _slugify(name: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", name.lower().strip())
    return re.sub(r"[\s_]+", "-", slug)[:50]


@router.get("/my", response_model=TenantResponse | None)
def get_my_tenant(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return the current user's tenant."""
    if not current_user.tenant_id:
        return None
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        return None
    return TenantResponse(
        id=tenant.id, name=tenant.name, slug=tenant.slug,
        created_at=str(tenant.created_at) if tenant.created_at else None,
    )


@router.get("/", response_model=list[TenantResponse])
def list_tenants(
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """List all tenants (admin/superadmin only)."""
    tenants = db.query(Tenant).order_by(Tenant.id).all()
    return [
        TenantResponse(
            id=t.id, name=t.name, slug=t.slug,
            created_at=str(t.created_at) if t.created_at else None,
        )
        for t in tenants
    ]


@router.post("/", response_model=TenantResponse, status_code=201)
def create_tenant(
    body: TenantCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    slug = body.slug or _slugify(body.name)
    if db.query(Tenant).filter(Tenant.slug == slug).first():
        raise HTTPException(status_code=409, detail="Тенант с таким slug уже существует")

    tenant = Tenant(name=body.name.strip(), slug=slug)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return TenantResponse(
        id=tenant.id, name=tenant.name, slug=tenant.slug,
        created_at=str(tenant.created_at) if tenant.created_at else None,
    )


@router.patch("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    body: TenantUpdate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Тенант не найден")

    if body.name is not None:
        tenant.name = body.name.strip()
    if body.slug is not None:
        existing = db.query(Tenant).filter(Tenant.slug == body.slug, Tenant.id != tenant_id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Slug уже занят")
        tenant.slug = body.slug

    db.commit()
    db.refresh(tenant)
    return TenantResponse(
        id=tenant.id, name=tenant.name, slug=tenant.slug,
        created_at=str(tenant.created_at) if tenant.created_at else None,
    )


@router.delete("/{tenant_id}", status_code=204)
def delete_tenant(
    tenant_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Только суперадмин может удалять тенанты")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Тенант не найден")
    db.delete(tenant)
    db.commit()
