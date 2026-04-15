"""Access credentials CRUD API."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.encryption import encrypt_password
from backend.models import User, AccessCredential

router = APIRouter()


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("superadmin", "admin"):
        raise HTTPException(403, "Manager access required")
    return current_user


class CredentialCreate(BaseModel):
    name: str
    domain: str = ""
    login: str = ""
    password: str = ""
    workspace: str = "Default workspace"


@router.get("/")
def list_credentials(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    creds = db.query(AccessCredential).order_by(AccessCredential.id).all()
    return [
        {"id": c.id, "name": c.name, "domain": c.domain, "login": c.login, "workspace": c.workspace}
        for c in creds
    ]


@router.post("/")
def create_credential(body: CredentialCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    cred = AccessCredential(
        name=body.name, domain=body.domain, login=body.login,
        password_encrypted=encrypt_password(body.password), workspace=body.workspace,
        created_by=current_user.id,
    )
    db.add(cred)
    db.commit()
    db.refresh(cred)
    return {"id": cred.id, "name": cred.name}


@router.put("/{cred_id}")
def update_credential(cred_id: int, body: CredentialCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    cred = db.query(AccessCredential).filter(AccessCredential.id == cred_id).first()
    if not cred:
        raise HTTPException(404, "Credential not found")
    cred.name = body.name
    cred.domain = body.domain
    cred.login = body.login
    if body.password:
        cred.password_encrypted = encrypt_password(body.password)
    cred.workspace = body.workspace
    db.commit()
    return {"id": cred.id, "name": cred.name}


@router.delete("/{cred_id}")
def delete_credential(cred_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    cred = db.query(AccessCredential).filter(AccessCredential.id == cred_id).first()
    if not cred:
        raise HTTPException(404, "Not found")
    db.delete(cred)
    db.commit()
    return {"status": "deleted"}
