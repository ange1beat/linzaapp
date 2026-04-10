from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from starlette.requests import Request

from app.db import get_all, update_all, seed_defaults, get_audit, DEFAULT_CONFIG

router = APIRouter()

VALID_CATEGORIES = {"prohibited", "18+", "16+"}
VALID_SUBCLASSES = {item[0] for item in DEFAULT_CONFIG}


class ClassifierItem(BaseModel):
    subclass: str = Field(..., min_length=1, max_length=50)
    category: str


@router.get("/")
def list_config():
    return get_all()


@router.put("/")
def update_config(items: list[ClassifierItem], request: Request):
    if len(items) > 100:
        raise HTTPException(400, "Too many items (max 100)")
    for item in items:
        if item.subclass not in VALID_SUBCLASSES:
            raise HTTPException(
                400, f"Unknown subclass '{item.subclass}'"
            )
        if item.category not in VALID_CATEGORIES:
            raise HTTPException(
                400, f"Invalid category '{item.category}' for subclass '{item.subclass}'"
            )
    update_all(
        [item.model_dump() for item in items],
        request_id=getattr(request.state, "request_id", ""),
    )
    return get_all()


@router.put("/reset")
def reset_config(request: Request):
    seed_defaults(request_id=getattr(request.state, "request_id", ""))
    return get_all()


@router.get("/audit")
def list_audit(
    subclass: str | None = None,
    action: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    return get_audit(subclass=subclass, action=action, limit=limit, offset=offset)
