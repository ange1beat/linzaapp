"""Build moderation prompts from user-defined categories (name + description)."""

from pydantic import BaseModel, Field, field_validator


class ModerationCategory(BaseModel):
    """One detectable category; `name` is the exact token the model must return as verdict."""

    name: str = Field(..., min_length=1, max_length=64, description="Short id, e.g. nude, violence")
    description: str = Field(..., min_length=1, max_length=4000, description="What this category means")

    @field_validator("name")
    @classmethod
    def name_trim(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("name cannot be empty")
        return s


def build_moderation_prompt(
    categories: list[ModerationCategory],
    *,
    extra_instructions: str | None = None,
) -> str:
    if not categories:
        raise ValueError("categories must be non-empty")

    names = [c.name for c in categories]
    names_lower = {n.lower() for n in names}
    if len(names_lower) != len(names):
        raise ValueError("category names must be unique (case-insensitive)")

    forbidden_literal = "none"
    name_list = ", ".join(f'"{n}"' for n in names)

    lines: list[str] = [
        "You review one still frame from a video.",
        "Your task: decide whether the frame shows any of the categories below.",
        "",
        "Categories (verdict token → meaning):",
    ]
    for c in categories:
        lines.append(f'- "{c.name}": {c.description.strip()}')
    lines.extend(
        [
            "",
            f'If none of these apply, verdict must be exactly "{forbidden_literal}" (no prohibited content).',
            f"If one or more apply, verdict must be exactly ONE token from this list: {name_list}.",
            "Pick the single most prominent / severe match. If several are equally clear, pick the worst.",
            "",
            "Output JSON only, no markdown fences. Schema:",
            '{"verdict": "<token>", "reason": "one short sentence"}',
            f'where <token> is either "{forbidden_literal}" or one of: {name_list}.',
        ]
    )
    if extra_instructions and extra_instructions.strip():
        lines.extend(["", "Additional instructions:", extra_instructions.strip()])
    return "\n".join(lines)


def build_transcript_moderation_prompt(
    categories: list[ModerationCategory],
    *,
    extra_instructions: str | None = None,
) -> str:
    """Same category tokens as vision, but for spoken transcript (ASR text)."""
    if not categories:
        raise ValueError("categories must be non-empty")

    names = [c.name for c in categories]
    names_lower = {n.lower() for n in names}
    if len(names_lower) != len(names):
        raise ValueError("category names must be unique (case-insensitive)")

    forbidden_literal = "none"
    name_list = ", ".join(f'"{n}"' for n in names)

    lines: list[str] = [
        "You review the transcript of spoken audio from a video (automatic speech recognition; text may contain errors).",
        "Decide whether anything said clearly falls under the categories below (advocacy, explicit description, instructions, slurs, etc.).",
        "",
        "Categories (verdict token → meaning):",
    ]
    for c in categories:
        lines.append(f'- "{c.name}": {c.description.strip()}')
    lines.extend(
        [
            "",
            f'If none apply, verdict must be exactly "{forbidden_literal}".',
            f"Otherwise verdict must be exactly ONE token from: {name_list} (worst / clearest match).",
            "",
            "Output JSON only, no markdown. Schema:",
            '{"verdict": "<token>", "reason": "one short sentence", "spans": [{"t_start_sec": number, "t_end_sec": number, "quote": "short excerpt"}]}',
            f'Use empty spans [] if verdict is "{forbidden_literal}". Otherwise cite 1–3 short time-bounded quotes when timestamps are given in the transcript.',
            f'where <token> is "{forbidden_literal}" or one of: {name_list}.',
        ]
    )
    if extra_instructions and extra_instructions.strip():
        lines.extend(["", "Additional instructions:", extra_instructions.strip()])
    return "\n".join(lines)
