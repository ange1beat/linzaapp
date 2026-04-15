"""Data sources CRUD API."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User, DataSource

router = APIRouter()


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("superadmin", "admin"):
        raise HTTPException(403, "Manager access required")
    return current_user


class SourceCreate(BaseModel):
    name: str
    path_type: str = "http"
    path_url: str = ""
    file_extensions: str = "mp4,avi,mkv,mov"
    priority: str = "Normal"
    access_credential_id: int | None = None
    workspace: str = "Default workspace"


@router.get("/")
def list_sources(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    sources = db.query(DataSource).order_by(DataSource.id).all()
    return [
        {
            "id": s.id, "name": s.name, "path_type": s.path_type,
            "path_url": s.path_url, "file_extensions": s.file_extensions,
            "priority": s.priority, "access_credential_id": s.access_credential_id,
            "workspace": s.workspace,
        }
        for s in sources
    ]


@router.post("/")
def create_source(body: SourceCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    src = DataSource(
        name=body.name, path_type=body.path_type, path_url=body.path_url,
        file_extensions=body.file_extensions, priority=body.priority,
        access_credential_id=body.access_credential_id, workspace=body.workspace,
        created_by=current_user.id,
    )
    db.add(src)
    db.commit()
    db.refresh(src)
    return {"id": src.id, "name": src.name}


@router.put("/{source_id}")
def update_source(source_id: int, body: SourceCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    src = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not src:
        raise HTTPException(404, "Source not found")
    src.name = body.name
    src.path_type = body.path_type
    src.path_url = body.path_url
    src.file_extensions = body.file_extensions
    src.priority = body.priority
    src.access_credential_id = body.access_credential_id
    src.workspace = body.workspace
    db.commit()
    return {"id": src.id, "name": src.name}


@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    src = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not src:
        raise HTTPException(404, "Not found")
    db.delete(src)
    db.commit()
    return {"status": "deleted"}
