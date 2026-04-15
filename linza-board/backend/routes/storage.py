"""Storage profile management API — role-based access."""

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User, StorageProfile

router = APIRouter()


# ── Dependencies ──────────────────────────────────────────────────────────────

def require_superadmin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "superadmin":
        raise HTTPException(403, "Superadmin access required")
    return current_user


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("superadmin", "admin"):
        raise HTTPException(403, "Manager access required")
    return current_user


# ── Request/Response models ───────────────────────────────────────────────────

class StorageProfileCreate(BaseModel):
    name: str
    profile_type: str  # "source" or "destination"
    s3_endpoint_url: str = ""
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket_name: str = ""
    s3_region: str = ""
    s3_tenant_id: str = ""


class StorageProfileUpdate(BaseModel):
    name: str | None = None
    s3_endpoint_url: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_bucket_name: str | None = None
    s3_region: str | None = None
    s3_tenant_id: str | None = None


class StorageProfileResponse(BaseModel):
    id: int
    name: str
    profile_type: str
    s3_endpoint_url: str
    s3_access_key_id: str  # masked
    s3_bucket_name: str
    s3_region: str
    s3_tenant_id: str
    is_active: bool

    class Config:
        from_attributes = True


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "***"
    return key[:8] + "..."


def _to_response(p: StorageProfile) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "profile_type": p.profile_type,
        "s3_endpoint_url": p.s3_endpoint_url,
        "s3_access_key_id": _mask_key(p.s3_access_key_id),
        "s3_bucket_name": p.s3_bucket_name,
        "s3_region": p.s3_region,
        "s3_tenant_id": p.s3_tenant_id,
        "is_active": p.is_active,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/")
@router.get("")
def list_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    profiles = db.query(StorageProfile).order_by(StorageProfile.id).all()
    return [_to_response(p) for p in profiles]


@router.post("/")
@router.post("")
def create_profile(
    body: StorageProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    if body.profile_type not in ("source", "destination"):
        raise HTTPException(400, "profile_type must be 'source' or 'destination'")
    ep = (body.s3_endpoint_url or "").strip().lower()
    if ep == "yandex-disk":
        if not (body.s3_secret_access_key or "").strip():
            raise HTTPException(400, "Для Яндекс.Диска укажите OAuth-токен (поле Secret)")
    profile = StorageProfile(
        name=body.name,
        profile_type=body.profile_type,
        s3_endpoint_url=body.s3_endpoint_url,
        s3_access_key_id=body.s3_access_key_id,
        s3_secret_access_key=body.s3_secret_access_key,
        s3_bucket_name=body.s3_bucket_name,
        s3_region=body.s3_region,
        s3_tenant_id=body.s3_tenant_id,
        created_by=current_user.id,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _to_response(profile)


@router.put("/{profile_id}")
def update_profile(
    profile_id: int,
    body: StorageProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    profile = db.query(StorageProfile).filter(StorageProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")

    # Admin can only update source profiles: endpoint_url + keys
    if current_user.role == "admin":
        if profile.profile_type != "source":
            raise HTTPException(403, "Admins can only edit source profiles")
        allowed = {"s3_endpoint_url", "s3_access_key_id", "s3_secret_access_key"}
        updates = body.model_dump(exclude_unset=True)
        forbidden = set(updates.keys()) - allowed
        if forbidden:
            raise HTTPException(403, f"Admins cannot change: {', '.join(forbidden)}")

    updates = body.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return _to_response(profile)


@router.delete("/{profile_id}")
def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    profile = db.query(StorageProfile).filter(StorageProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")
    if profile.is_active:
        raise HTTPException(400, "Cannot delete active profile. Deactivate first.")
    db.delete(profile)
    db.commit()
    return {"status": "deleted"}


@router.post("/{profile_id}/activate")
def activate_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    profile = db.query(StorageProfile).filter(StorageProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")

    # Deactivate other profiles of same type
    db.query(StorageProfile).filter(
        StorageProfile.profile_type == profile.profile_type,
        StorageProfile.id != profile_id,
    ).update({"is_active": False})

    profile.is_active = True
    db.commit()
    return _to_response(profile)


@router.post("/{profile_id}/test")
def test_connection(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    profile = db.query(StorageProfile).filter(StorageProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")

    ep = (profile.s3_endpoint_url or "").strip().lower()
    if ep == "yandex-disk":
        if not (profile.s3_secret_access_key or "").strip():
            raise HTTPException(400, "Укажите OAuth-токен Яндекс.Диска")
        try:
            r = httpx.get(
                "https://cloud-api.yandex.net/v1/disk",
                headers={"Authorization": f"OAuth {profile.s3_secret_access_key.strip()}"},
                timeout=30.0,
            )
            if r.status_code == 401:
                raise HTTPException(502, "Неверный или просроченный OAuth-токен Яндекс")
            r.raise_for_status()
            data = r.json()
            used = data.get("used_space")
            total = data.get("total_space")
            hint = profile.s3_bucket_name or "все видео/аудио на Диске"
            return {
                "status": "ok",
                "bucket": hint,
                "objects": 0,
                "yandex": True,
                "used_space": used,
                "total_space": total,
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(502, f"Яндекс.Диск: {e}") from e

    import boto3
    from botocore.config import Config

    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=profile.s3_access_key_id,
            aws_secret_access_key=profile.s3_secret_access_key,
            endpoint_url=profile.s3_endpoint_url,
            region_name=profile.s3_region,
            config=Config(signature_version="s3v4"),
        )
        resp = client.list_objects_v2(Bucket=profile.s3_bucket_name, MaxKeys=1)
        return {"status": "ok", "bucket": profile.s3_bucket_name, "objects": resp.get("KeyCount", 0)}
    except Exception as e:
        raise HTTPException(502, f"Connection failed: {e}")
