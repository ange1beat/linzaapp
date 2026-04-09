"""Load stored categories JSON from a job row."""

from __future__ import annotations

import json
from typing import Any

from pydantic import TypeAdapter

from app.prompt_builder import ModerationCategory


def categories_from_job_row(row: dict[str, Any]) -> list[ModerationCategory] | None:
    raw = row.get("categories_json")
    if raw is None or not str(raw).strip():
        return None
    try:
        return TypeAdapter(list[ModerationCategory]).validate_json(raw)
    except Exception:
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return TypeAdapter(list[ModerationCategory]).validate_python(data)
        except Exception:
            pass
    return None
