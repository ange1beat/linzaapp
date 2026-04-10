"""Стандартный классификатор Linza: типы контента, подклассы K1–K7, матрица уровней."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from app.prompt_builder import ModerationCategory

CONTENT_TYPES: list[dict[str, str]] = [
    {"id": "art", "label": "◆ Художественное кино и сериалы", "short": "Худож. кино"},
    {"id": "doc", "label": "▣ Документальное кино", "short": "Док. кино"},
    {"id": "ad", "label": "● Реклама (вкл. трейлеры)", "short": "Реклама"},
    {"id": "arch", "label": "◇ Архивный контент (до 1991)", "short": "Архив"},
]

LEGEND: list[dict[str, str]] = [
    {"symbol": "⛔", "meaning": "Запрет"},
    {"symbol": "⚠️", "meaning": "Маркировка"},
    {"symbol": "✓", "meaning": "Проверка"},
    {"symbol": "◈", "meaning": "Особое"},
    {"symbol": "🛡", "meaning": "Исключение ИХЦ"},
    {"symbol": "—", "meaning": "Не применимо"},
]

_SYMBOL_MEANING: dict[str, str] = {x["symbol"]: x["meaning"] for x in LEGEND}

# Шаблон из исходной таблицы (заголовки колонок и легенда — как у вас в сообщении).
LINZA_MATRIX_HEADER_ROW = (
    "ПОДКЛАСС\t◆ ХУДОЖ. КИНО И СЕРИАЛЫ\t▣ ДОКУМЕНТАЛЬНОЕ КИНО\t"
    "● РЕКЛАМА (ВКЛ. ТРЕЙЛЕРЫ)\t◇ АРХИВНЫЙ (ДО 1991)"
)

LINZA_LEGEND_TEXT = """⛔ Запрет
⚠️ Маркировка
✓ Проверка
◈ Особое
🛡 Исключение ИХЦ
— Не применимо"""


def _unique_chapters_ordered() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for ch, ch_title, *_ in _RULES_RAW:
        key = (ch, ch_title)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def build_full_linza_classification_text() -> str:
    """Весь справочник Linza: типы контента, легенда, матрица и все подклассы с id (k1_1 …)."""
    ct_lines = "\n".join(f"- {x['id']}: {x['label']}" for x in CONTENT_TYPES)
    rule_lines: list[str] = []
    for r in LINZA_RULES:
        m = r["matrix"]
        assert isinstance(m, dict)
        rule_lines.append(
            f"- {r['id']}: [{r['chapter']} {r['code']}] {r['title']}\n"
            f"  Матрица (худож.|док.|рекл.|архив): {m.get('art', '—')} | {m.get('doc', '—')} | "
            f"{m.get('ad', '—')} | {m.get('arch', '—')}"
        )
    rules_block = "\n".join(rule_lines)
    chapters = "\n".join(f"{ch} · {title}" for ch, title in _unique_chapters_ordered())
    return (
        "### Типы контента (колонки матрицы)\n"
        f"{ct_lines}\n\n"
        "### Легенда символов матрицы\n"
        f"{LINZA_LEGEND_TEXT}\n\n"
        "### Строка заголовков матрицы (подкласс × тип контента)\n"
        f"{LINZA_MATRIX_HEADER_ROW}\n\n"
        "### Оглавление разделов K1–K7\n"
        f"{chapters}\n\n"
        "### Полный перечень подклассов\n"
        "Поле `verdict` в ответе — ровно значение `id` строки (например k2_2) либо none.\n\n"
        f"{rules_block}"
    )


def build_default_server_prompt_with_full_linza() -> str:
    """Стандартный промпт модерации кадра с полной классификацией Linza (для Settings.default_prompt)."""
    return (
        "Ты модератор контента. Ты видишь один статичный кадр из видео.\n"
        "Ответ строго одним JSON-объектом, без markdown и без пояснений вне JSON:\n"
        '{"verdict": "none" или id подкласса Linza (например k1_3, k2_2), "reason": "краткое пояснение на русском или английском"}\n'
        'Используй verdict "none", если на кадре ни один подкласс из справочника ниже явно не подтверждён. '
        "Не придумывай нарушения и не смешивай несколько id в одном вердикте — только один токен или none.\n\n"
        "### Классификатор Linza (полный)\n\n"
        f"{build_full_linza_classification_text()}"
    )


def build_default_transcript_moderation_prompt_with_full_linza() -> str:
    """Промпт модерации расшифровки речи: те же id Linza, что и для кадров + spans по времени."""
    return (
        "Ты модератор контента. На входе — расшифровка речи из видео (ASR; возможны ошибки распознавания и пунктуации).\n"
        "Сопоставь смысл речи с подклассами Linza ниже. Ответ строго одним JSON-объектом, без markdown:\n"
        '{"verdict": "none" или один id подкласса Linza (например k2_2, k3_3), '
        '"reason": "краткое пояснение", '
        '"spans": [{"start": <секунды float>, "end": <секунды float>, "quote": "фрагмент текста или пустая строка"}]'
        "}\n"
        "Правила: если нарушений по справочнику нет — verdict \"none\" и spans []. "
        "Если есть нарушение — выбери один наиболее подходящий id; в spans перечисли интервалы (по таймкодам из блока "
        "### Segments, если он есть, иначе оцени по контексту). Не выдумывай нарушения.\n\n"
        "### Классификатор Linza (полный)\n\n"
        f"{build_full_linza_classification_text()}"
    )


def build_linza_prompt_preamble(content_type_id: str) -> str:
    """Текст, который вставляется в промпт перед блоком категорий, если задействован Linza."""
    ct = content_type_id.strip()
    valid_ct = {x["id"] for x in CONTENT_TYPES}
    if ct not in valid_ct:
        ct = "doc"
    ct_label = next(x["label"] for x in CONTENT_TYPES if x["id"] == ct)
    chapters = "\n".join(f"{ch} · {title}" for ch, title in _unique_chapters_ordered())
    return (
        "### Классификатор Linza — матрица и легенда\n\n"
        "Строки таблицы — подклассы (ниже в промпте перечислены только выбранные для этой задачи). "
        "Колонки — тип контента; для каждой ячейки задан уровень требования.\n\n"
        f"{LINZA_MATRIX_HEADER_ROW}\n\n"
        f"{LINZA_LEGEND_TEXT}\n\n"
        f"Активная колонка (тип контента материала для этой проверки): {ct_label}\n\n"
        "Инструкция по кадру: ты видишь один статичный кадр из видео. "
        "Сопоставь изображение с описаниями выбранных подклассов ниже; в каждом описании указан символ матрицы "
        "и его смысл для активного типа контента. "
        "Вердикт в JSON — ровно один токен `verdict` из имён категорий (например k1_1) либо none, "
        "если ни один подкласс явно не подтверждён. Не придумывай нарушения.\n\n"
        "Разделы справочника K1–K7 (для контекста):\n"
        f"{chapters}"
    )


def _m(art: str, doc: str, ad: str, arch: str) -> dict[str, str]:
    return {"art": art, "doc": doc, "ad": ad, "arch": arch}


# matrix keys: art, doc, ad, arch — как в исходной таблице
_RULES_RAW: list[tuple[str, str, str, str, dict[str, str]]] = [
    ("K1", "Наркотические вещества, курение, инъекции, алкоголь", "1.1", "Демонстрация табачных / курительных изделий", _m("⚠️", "⚠️", "⛔", "🛡")),
    ("K1", "Наркотические вещества, курение, инъекции, алкоголь", "1.2", "Демонстрация алкоголя в рекламном контексте", _m("⚠️", "⚠️", "◈", "🛡")),
    ("K1", "Наркотические вещества, курение, инъекции, алкоголь", "1.3", "Демонстрация / пропаганда веществ, изменяющих сознание", _m("⛔", "⛔", "⛔", "◈")),
    ("K1", "Наркотические вещества, курение, инъекции, алкоголь", "1.4", "Вовлечение н/л в употребление запрещённых веществ", _m("⛔", "⛔", "⛔", "⛔")),
    ("K2", "Девиантное и асоциальное поведение", "2.1", "Воровство, разбой, вандализм — романтизация", _m("✓", "✓", "✓", "🛡")),
    ("K2", "Девиантное и асоциальное поведение", "2.2", "Нецензурная брань / ненормативная лексика", _m("⚠️", "⚠️", "⛔", "🛡")),
    ("K2", "Девиантное и асоциальное поведение", "2.3", "Призывы к насилию / разжигание ненависти", _m("⛔", "⛔", "⛔", "⛔")),
    ("K2", "Девиантное и асоциальное поведение", "2.4", "Психологическое давление: травля, буллинг, запугивание", _m("✓", "✓", "✓", "✓")),
    ("K2", "Девиантное и асоциальное поведение", "2.5", "Насилие в отношении детей", _m("⛔", "⛔", "⛔", "⛔")),
    ("K2", "Девиантное и асоциальное поведение", "2.6", "Побуждение детей к суициду / причинению вреда здоровью", _m("⛔", "⛔", "⛔", "⛔")),
    ("K3", "Терроризм, экстремизм, нацизм — КоАП ст.20.3", "3.1", "Нацистская символика и атрибутика", _m("◈", "◈", "⛔", "🛡")),
    ("K3", "Терроризм, экстремизм, нацизм — КоАП ст.20.3", "3.2", "Реабилитация нацизма / фальсификация истории ВОВ", _m("⛔", "⛔", "⛔", "⛔")),
    ("K3", "Терроризм, экстремизм, нацизм — КоАП ст.20.3", "3.3", "Пропаганда терроризма и запрещённых организаций", _m("⛔", "⛔", "⛔", "⛔")),
    ("K3", "Терроризм, экстремизм, нацизм — КоАП ст.20.3", "3.4", "Дискредитация ВС РФ / фейки о деятельности армии", _m("⛔", "⛔", "⛔", "✓")),
    ("K3", "Терроризм, экстремизм, нацизм — КоАП ст.20.3", "3.5", "Призывы к массовым беспорядкам / экстремизму", _m("⛔", "⛔", "⛔", "⛔")),
    ("K4", "Эротика / порнография", "4.1", "Информация эротического характера", _m("⚠️", "⚠️", "⛔", "⚠️")),
    ("K4", "Эротика / порнография", "4.2", "Информация порнографического характера (незаконный оборот)", _m("⛔", "⛔", "⛔", "⛔")),
    ("K4", "Эротика / порнография", "4.3", "Детская порнография / педофилия", _m("⛔", "⛔", "⛔", "⛔")),
    ("K5", "Уничижение традиций и семейных ценностей", "5.1", "Пропаганда ЛГБТ+ отношений и идентичности", _m("⛔", "⛔", "⛔", "🛡")),
    ("K5", "Уничижение традиций и семейных ценностей", "5.2", "Пропаганда смены пола / трансгендерности", _m("⛔", "⛔", "⛔", "🛡")),
    ("K5", "Уничижение традиций и семейных ценностей", "5.3", "Пропаганда отказа от деторождения (чайлдфри)", _m("⛔", "⛔", "⛔", "✓")),
    ("K5", "Уничижение традиций и семейных ценностей", "5.4", "Пропаганда педофилии", _m("⛔", "⛔", "⛔", "⛔")),
    ("K5", "Уничижение традиций и семейных ценностей", "5.5", "Дискредитация института семьи и традиционных ценностей", _m("⛔", "◈", "✓", "🛡")),
    ("K6", "Антипатриотический контент: иноагенты, реклама, религия", "6.1", "Нарушение требований к материалам иностранных агентов", _m("✓", "✓", "⛔", "—")),
    ("K6", "Антипатриотический контент: иноагенты, реклама, религия", "6.2", "Нарушения в рекламе: ЕРИР, запрещённые ресурсы", _m("—", "—", "⛔", "—")),
    ("K6", "Антипатриотический контент: иноагенты, реклама, религия", "6.3", "Оскорбление религиозных чувств / дискредитация традиций", _m("⛔", "⛔", "⛔", "◈")),
    ("K7", "Тотализаторы, букмекеры, казино — лудомания", "7.1", "Реклама и продвижение нелегальных онлайн-казино", _m("—", "—", "⛔", "—")),
    ("K7", "Тотализаторы, букмекеры, казино — лудомания", "7.2", "Реклама букмекеров и тотализаторов с нарушениями", _m("—", "—", "⛔", "—")),
    ("K7", "Тотализаторы, букмекеры, казино — лудомания", "7.3", "Вовлечение несовершеннолетних в азартные игры", _m("⛔", "⛔", "⛔", "⛔")),
    ("K7", "Тотализаторы, букмекеры, казино — лудомания", "7.4", "Пропаганда лудомании / симуляторы казино без лицензии", _m("—", "✓", "✓", "—")),
]

LINZA_RULES: list[dict[str, object]] = []
_RULE_BY_ID: dict[str, dict[str, object]] = {}

for ch, ch_title, code, title, matrix in _RULES_RAW:
    mch = re.match(r"K(\d+)$", ch.strip())
    chap_n = mch.group(1) if mch else ch.lower().lstrip("k")
    sub_n = code.split(".")[-1] if "." in code else code
    rid = f"k{chap_n}_{sub_n}"
    blob = f"{rid} {ch} {ch_title} {code} {title}".lower()
    row = {
        "id": rid,
        "chapter": ch,
        "chapter_title": ch_title,
        "code": code,
        "title": title,
        "matrix": matrix,
        "search_text": blob,
    }
    LINZA_RULES.append(row)
    _RULE_BY_ID[rid] = row


def linza_rule_by_verdict(verdict: str) -> dict[str, object] | None:
    """Справочник Linza по токену вердикта (например k2_2)."""
    v = (verdict or "").strip().lower()
    r = _RULE_BY_ID.get(v)
    return dict(r) if r else None


class LinzaSelection(BaseModel):
    """Выбор подклассов под конкретный тип контента (колонка матрицы)."""

    content_type_id: str = Field(..., min_length=1, description="art | doc | ad | arch")
    rule_ids: list[str] = Field(..., min_length=1)


def taxonomy_payload() -> dict[str, object]:
    return {
        "content_types": CONTENT_TYPES,
        "legend": LEGEND,
        "rules": LINZA_RULES,
        "prompt_template_note": (
            "Для каждого выбранного подкласса вердикт модели — это поле id (например k1_1). "
            "В описании указан уровень требования для выбранного типа контента."
        ),
        "matrix_header_row": LINZA_MATRIX_HEADER_ROW,
        "legend_text": LINZA_LEGEND_TEXT,
        "prompt_preamble_example_doc": build_linza_prompt_preamble("doc"),
    }


def search_rules(query: str, *, limit: int = 80) -> list[dict[str, object]]:
    q = (query or "").strip().lower()
    if not q:
        return list(LINZA_RULES[:limit])
    out: list[dict[str, object]] = []
    for r in LINZA_RULES:
        if q in str(r["search_text"]) or q in str(r["id"]):
            out.append(r)
        if len(out) >= limit:
            break
    return out


def _symbol_meaning(sym: str) -> str:
    return _SYMBOL_MEANING.get(sym, sym)


def linza_to_categories(sel: LinzaSelection) -> list[ModerationCategory]:
    ct = sel.content_type_id.strip()
    valid_ct = {x["id"] for x in CONTENT_TYPES}
    if ct not in valid_ct:
        raise ValueError(f"Unknown content_type_id: {ct!r}; expected one of {sorted(valid_ct)}")

    ct_label = next(x["label"] for x in CONTENT_TYPES if x["id"] == ct)
    out: list[ModerationCategory] = []
    for rid in sel.rule_ids:
        rule = _RULE_BY_ID.get(rid.strip())
        if rule is None:
            raise ValueError(f"Unknown rule id: {rid!r}")

        matrix = rule["matrix"]
        assert isinstance(matrix, dict)
        sym = str(matrix.get(ct, "—"))
        if sym == "—":
            continue

        meaning = _symbol_meaning(sym)
        desc = (
            f"Классификатор Linza, тип контента: {ct_label}. "
            f"Раздел {rule['chapter']} ({rule['chapter_title']}). "
            f"Пункт {rule['code']}: {rule['title']}. "
            f"Для этого типа контента уровень в матрице: {sym} ({meaning}). "
            f"Отмечай кадр этим вердиктом только при явном соответствии смыслу пункта."
        )
        out.append(ModerationCategory(name=str(rule["id"]), description=desc))

    if not out:
        raise ValueError(
            "После фильтрации не осталось правил: для выбранного типа контента все пункты «не применимо» (—). "
            "Выберите другие подклассы или другой тип контента."
        )
    return out


def format_linza_context_for_report(sel: LinzaSelection | None) -> str | None:
    if sel is None:
        return None
    ct_label = next((x["label"] for x in CONTENT_TYPES if x["id"] == sel.content_type_id), sel.content_type_id)
    lines = [f"Тип контента: {ct_label}", "Выбранные подклассы:"]
    for rid in sel.rule_ids:
        r = _RULE_BY_ID.get(rid)
        if not r:
            lines.append(f"  — {rid} (неизвестный id)")
            continue
        matrix = r["matrix"]
        assert isinstance(matrix, dict)
        sym = matrix.get(sel.content_type_id, "—")
        lines.append(f"  — {r['code']} {r['title']} [{sym}]")
    return "\n".join(lines)
