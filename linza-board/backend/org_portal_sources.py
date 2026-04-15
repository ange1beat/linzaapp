"""Источники загрузки из org-config (мастер администратора) — для UI и проверок API."""

from __future__ import annotations

import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models import AppSetting

ORG_CONFIG_KEY = "org_portal_config"

# Совпадает с WIZARD_SOURCES в adminWizardCatalog.js
_ALLOWED = frozenset({"local", "yadisk", "google", "s3"})

# Если конфиг пуст — все способы доступны (обратная совместимость)
_DEFAULT_ENABLED = ["local", "yadisk", "google", "s3"]


def get_sources_enabled(db: Session) -> list[str]:
    row = db.query(AppSetting).filter(AppSetting.key == ORG_CONFIG_KEY).first()
    if not row or not (row.value or "").strip():
        return list(_DEFAULT_ENABLED)
    try:
        data = json.loads(row.value)
    except json.JSONDecodeError:
        return list(_DEFAULT_ENABLED)
    raw = data.get("sources_enabled") or data.get("sourcesEnabled")
    if not isinstance(raw, list) or not raw:
        return list(_DEFAULT_ENABLED)
    mapped: list[str] = []
    for x in raw:
        if not isinstance(x, str):
            continue
        s = "yadisk" if x.strip().lower() == "yandex" else x.strip()
        if s in _ALLOWED:
            mapped.append(s)
    return mapped if mapped else ["local"]


def assert_ingest_sources_allowed(db: Session, *required: str) -> None:
    """403, если хотя бы один из required не включён в org-config."""
    if not required:
        return
    enabled = set(get_sources_enabled(db))
    if all(r in enabled for r in required):
        return
    raise HTTPException(
        status_code=403,
        detail="Этот способ загрузки отключён в настройках организации (мастер администратора).",
    )
