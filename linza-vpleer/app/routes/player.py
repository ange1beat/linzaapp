"""Встроенный HTML-видеоплеер и список файлов."""

import html
import json
from pathlib import Path
from urllib.parse import quote

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import STORAGE_SERVICE_URL
from app.storage_http import storage_request_headers

router = APIRouter(prefix="/api/vpleer", tags=["player"])

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


@router.get("/files")
async def list_files():
    """Список видеофайлов из хранилища."""
    try:
        h = storage_request_headers()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{STORAGE_SERVICE_URL}/api/files", headers=h)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError:
        raise HTTPException(502, "Не удалось получить список файлов из хранилища")
    return data.get("files", [])


@router.get("/player/{filename:path}", response_class=HTMLResponse)
async def player_page(request: Request, filename: str, detections: str = None):
    """HTML-страница видеоплеера для встраивания и прямого просмотра."""
    return templates.TemplateResponse(request, "player.html", {
        "safe_name": html.escape(filename),
        "js_name": json.dumps(filename),
        "url_name": quote(filename, safe="/"),
    })


@router.get("/player", response_class=HTMLResponse)
async def player_index(request: Request):
    """Список файлов с ссылками на плеер."""
    try:
        h = storage_request_headers()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{STORAGE_SERVICE_URL}/api/files", headers=h)
            resp.raise_for_status()
            files = resp.json().get("files", [])
    except httpx.HTTPError:
        files = []
    return templates.TemplateResponse(request, "index.html", {
        "files": files,
    })
