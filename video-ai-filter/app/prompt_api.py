from typing import Annotated

from fastapi import HTTPException
from pydantic import BaseModel, Field, TypeAdapter

from app.config import Settings
from app.linza_taxonomy import LinzaSelection, build_linza_prompt_preamble, linza_to_categories
from app.prompt_builder import ModerationCategory, build_moderation_prompt


class PromptPreviewRequest(BaseModel):
    categories: list[ModerationCategory] | None = None
    linza: LinzaSelection | None = None
    extra_instructions: str | None = None


class PromptPreviewResponse(BaseModel):
    prompt: str


def parse_linza_json(raw: str | None) -> LinzaSelection | None:
    if raw is None or not str(raw).strip():
        return None
    try:
        return LinzaSelection.model_validate_json(str(raw).strip())
    except Exception as e:
        raise HTTPException(400, f"Invalid linza JSON: {e}") from e


def parse_categories_json(raw: str | None) -> list[ModerationCategory] | None:
    if raw is None or not str(raw).strip():
        return None
    try:
        return TypeAdapter(list[ModerationCategory]).validate_json(raw)
    except Exception as e:
        raise HTTPException(400, f"Invalid categories JSON: {e}") from e


def _merge_category_lists(
    categories: list[ModerationCategory] | None,
    linza: LinzaSelection | None,
) -> list[ModerationCategory]:
    merged: list[ModerationCategory] = []
    if categories:
        merged.extend(categories)
    if linza is not None:
        try:
            merged.extend(linza_to_categories(linza))
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
    seen: set[str] = set()
    deduped: list[ModerationCategory] = []
    for c in merged:
        k = c.name.lower()
        if k in seen:
            continue
        seen.add(k)
        deduped.append(c)
    return deduped


def resolve_effective_prompt(
    settings: Settings,
    prompt: str | None,
    categories: list[ModerationCategory] | None,
    linza: LinzaSelection | None = None,
) -> str:
    stripped = (prompt or "").strip()
    merged = _merge_category_lists(categories, linza)
    if merged:
        try:
            extra_parts: list[str] = []
            if linza is not None:
                extra_parts.append(build_linza_prompt_preamble(linza.content_type_id))
            if stripped:
                extra_parts.append(stripped)
            combined_extra = "\n\n".join(extra_parts) if extra_parts else None
            return build_moderation_prompt(
                merged,
                extra_instructions=combined_extra,
            )
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
    if stripped:
        return stripped
    return settings.default_prompt
