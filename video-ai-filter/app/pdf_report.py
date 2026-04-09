"""PDF-отчёт: шапка Linza, метаданные, сводка нарушений (видео + аудио), без промпта и сырого JSON."""

from __future__ import annotations

import time
from collections import Counter
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.export_util import parse_audio_results
from app.linza_taxonomy import CONTENT_TYPES, LinzaSelection, linza_rule_by_verdict
from app.time_report import _is_clean, _subclass_from_row, build_time_based_report

_DEJAVU_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
    Path("/opt/homebrew/share/fonts/dejavu-fonts/ttf/DejaVuSans.ttf"),
    Path("/usr/local/share/fonts/dejavu-fonts/ttf/DejaVuSans.ttf"),
)
_DEJAVU_BOLD_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"),
    Path("/opt/homebrew/share/fonts/dejavu-fonts/ttf/DejaVuSans-Bold.ttf"),
    Path("/usr/local/share/fonts/dejavu-fonts/ttf/DejaVuSans-Bold.ttf"),
)
_FONT = "Helvetica"
_FONT_BOLD = "Helvetica-Bold"

_NAVY = colors.HexColor("#0f172a")
_SLATE = colors.HexColor("#64748b")
_GREEN_BG = colors.HexColor("#dcfce7")
_GREEN_FG = colors.HexColor("#166534")
_RED_BG = colors.HexColor("#fee2e2")
_RED_FG = colors.HexColor("#b91c1c")
_BLUE_HEAD = colors.HexColor("#1e40af")
_BLUE_SOFT = colors.HexColor("#e0e7ff")


def _first_existing(candidates: tuple[Path, ...]) -> Path | None:
    for p in candidates:
        if p.is_file():
            return p
    return None


def _ensure_cyrillic_font() -> None:
    global _FONT, _FONT_BOLD
    if _FONT == "DejaVu":
        return
    dejavu = _first_existing(_DEJAVU_CANDIDATES)
    dejavu_bold = _first_existing(_DEJAVU_BOLD_CANDIDATES)
    if dejavu:
        pdfmetrics.registerFont(TTFont("DejaVu", str(dejavu)))
        _FONT = "DejaVu"
    if dejavu_bold:
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(dejavu_bold)))
        _FONT_BOLD = "DejaVu-Bold"
    else:
        _FONT_BOLD = _FONT


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def _format_duration_hms(total_sec: float) -> str:
    s = max(0, int(round(total_sec)))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h > 0:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"


def _estimate_duration_sec(
    results: list[dict[str, Any]],
    row: dict[str, Any],
    audio: dict[str, Any] | None,
) -> float:
    t_max = 0.0
    for r in results:
        try:
            t_max = max(t_max, float(r.get("time_sec") or 0))
        except (TypeError, ValueError):
            pass
    if audio and isinstance(audio.get("duration"), (int, float)):
        t_max = max(t_max, float(audio["duration"]))
    fps = row.get("video_fps")
    fc = row.get("video_frame_count")
    try:
        fps_f = float(fps) if fps is not None and float(fps) > 0 else None
        fc_i = int(fc) if fc is not None and int(fc) > 0 else None
        if fps_f and fc_i:
            t_max = max(t_max, fc_i / fps_f)
    except (TypeError, ValueError):
        pass
    return t_max


def _reason_from_frame_row(r: dict[str, Any]) -> str:
    p = r.get("verdict_parsed")
    if isinstance(p, dict) and p.get("reason") is not None:
        return str(p.get("reason", "")).strip()[:900]
    return ""


def _draw_page_number_canvas(canvas: Any, fn: str) -> None:
    """Номер страницы в углу (шрифт с кириллицей для «стр.»)."""
    try:
        pw, ph = canvas._pagesize  # noqa: SLF001
    except Exception:
        return
    canvas.saveState()
    canvas.setFont(fn, 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawRightString(pw - 1.0 * cm, ph - 0.55 * cm, f"стр. {canvas.getPageNumber()}")
    canvas.restoreState()


def _build_title_banner_flowable(
    content_width: float,
    fn: str,
    fn_b: str,
    styles: Any,
) -> Table:
    """Шапка в потоке platypus: только текст LINZA / DETECTOR (без растрового лого)."""
    reg = set(pdfmetrics.getRegisteredFontNames())
    if fn_b not in reg:
        fn_b = fn if fn in reg else fn_b
    sty_linza = ParagraphStyle(
        "pdf_linza",
        parent=styles["Normal"],
        fontName=fn_b,
        fontSize=32,
        leading=36,
        textColor=colors.white,
        alignment=1,
    )
    sty_det = ParagraphStyle(
        "pdf_det",
        parent=styles["Normal"],
        fontName=fn_b,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#93c5fd"),
        alignment=1,
    )
    sty_sub = ParagraphStyle(
        "pdf_sub",
        parent=styles["Normal"],
        fontName=fn,
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1,
    )
    text_col_w = max(content_width, 8 * cm)
    # Вложенная таблица: в ячейке Table допустимы только flowables с .draw()
    title_col = Table(
        [
            [Paragraph("LINZA", sty_linza)],
            [Spacer(1, 0.06 * cm)],
            [Paragraph("DETECTOR", sty_det)],
            [Spacer(1, 0.1 * cm)],
            [Paragraph("Структурированный отчёт по видеофайлу", sty_sub)],
        ],
        colWidths=[text_col_w],
    )
    title_col.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )

    inner = Table(
        [[title_col]],
        colWidths=[text_col_w],
    )
    inner.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    outer = Table([[inner]], colWidths=[content_width], rowHeights=[3.55 * cm])
    outer.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), _NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return outer


def _draw_footer(canvas: Any, page_w: float, job_id: str, fn: str) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.setLineWidth(0.35)
    canvas.line(1 * cm, 1.0 * cm, page_w - 1 * cm, 1.0 * cm)
    canvas.setFont(fn, 7.5)
    canvas.setFillColor(_SLATE)
    canvas.drawString(1 * cm, 0.55 * cm, f"Linza Detector · задание {job_id}")
    canvas.restoreState()


def build_job_pdf_bytes(
    *,
    job_id: str,
    row: dict[str, Any],
    results: list[dict[str, Any]],
    logo_path: Path | None = None,
) -> bytes:
    _ensure_cyrillic_font()
    fn = _FONT
    fn_b = _FONT_BOLD
    _reg = set(pdfmetrics.getRegisteredFontNames())
    if fn_b not in _reg and fn in _reg:
        fn_b = fn
    styles = getSampleStyleSheet()
    body = ParagraphStyle("B", parent=styles["Normal"], fontName=fn, fontSize=9, leading=12)
    small = ParagraphStyle("S", parent=styles["Normal"], fontName=fn, fontSize=8, leading=10)
    label_style = ParagraphStyle("L", parent=styles["Normal"], fontName=fn, fontSize=8.5, textColor=_SLATE)
    value_style = ParagraphStyle("V", parent=styles["Normal"], fontName=fn_b, fontSize=9.5, leading=12)

    fc = row.get("video_frame_count")
    fps = row.get("video_fps")
    try:
        fc_i = int(fc) if fc is not None and int(fc) > 0 else None
    except (TypeError, ValueError):
        fc_i = None
    try:
        fps_f = float(fps) if fps is not None and float(fps) > 0 else None
    except (TypeError, ValueError):
        fps_f = None

    audio = parse_audio_results(row)
    report = build_time_based_report(
        results,
        frame_count=fc_i,
        fps=fps_f,
        job_id=job_id,
        audio=audio,
    )
    dets: list[dict[str, Any]] = list(report.get("detections") or [])
    has_issues = len(dets) > 0

    linza_sel: LinzaSelection | None = None
    raw_linza = row.get("linza_selection_json")
    if raw_linza:
        try:
            linza_sel = LinzaSelection.model_validate_json(raw_linza)
        except Exception:
            pass

    buf = BytesIO()
    page_w, page_h = A4
    content_w = page_w - 2 * 1.15 * cm

    def on_page(canvas: Any, doc: Any) -> None:
        _draw_page_number_canvas(canvas, fn)
        _draw_footer(canvas, page_w, job_id, fn)

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.15 * cm,
        rightMargin=1.15 * cm,
        topMargin=1.05 * cm,
        bottomMargin=1.35 * cm,
        onFirstPage=on_page,
        onLaterPages=on_page,
    )

    vp = row.get("video_path") or ""
    source_name = Path(str(vp)).name if vp else "—"
    dur_sec = _estimate_duration_sec(results, row, audio)
    dur_str = _format_duration_hms(dur_sec) if dur_sec > 0 else "—"

    up = row.get("updated_at")
    cr = row.get("created_at")
    analysis_ts = "—"
    if isinstance(up, (int, float)):
        analysis_ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(up))
    proc_str = "—"
    if isinstance(cr, (int, float)) and isinstance(up, (int, float)) and up >= cr:
        proc_min = (up - cr) / 60.0
        if proc_min < 1:
            proc_str = f"{up - cr:.0f} с"
        else:
            proc_str = f"{proc_min:.1f} мин"

    meta_data = [
        [_p("Источник", label_style), _p(source_name, value_style)],
        [_p("Длительность (оценка)", label_style), _p(dur_str, value_style)],
        [_p("Дата анализа", label_style), _p(analysis_ts, value_style)],
        [_p("Время обработки", label_style), _p(proc_str, value_style)],
        [_p("Сэмплов кадров", label_style), _p(str(len(results)), value_style)],
    ]
    meta_tbl = Table(meta_data, colWidths=[4.5 * cm, content_w - 4.5 * cm])
    meta_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.HexColor("#e2e8f0")),
            ]
        )
    )

    tbl_cell = ParagraphStyle(
        "tbl_cell",
        parent=styles["Normal"],
        fontName=fn,
        fontSize=7.5,
        leading=10,
    )
    tbl_head_on_blue = ParagraphStyle(
        "tbl_head_on_blue",
        parent=styles["Normal"],
        fontName=fn_b,
        fontSize=7.5,
        leading=10,
        textColor=colors.white,
    )

    story: list[Any] = [
        _build_title_banner_flowable(content_w, fn, fn_b, styles),
        Spacer(1, 0.35 * cm),
        meta_tbl,
        Spacer(1, 0.45 * cm),
    ]

    if has_issues:
        ban = Table(
            [[_p("⚠ Обнаружены нарушения (видео и/или речь)", ParagraphStyle(
                "ban",
                parent=styles["Normal"],
                fontName=fn_b,
                fontSize=11,
                textColor=_RED_FG,
                alignment=1,
            ))]],
            colWidths=[content_w],
        )
        ban.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), _RED_BG),
                    ("BOX", (0, 0), (-1, -1), 0.8, _RED_FG),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
    else:
        ban = Table(
            [[_p("Нарушения по результатам анализа не выявлены", ParagraphStyle(
                "ok",
                parent=styles["Normal"],
                fontName=fn_b,
                fontSize=11,
                textColor=_GREEN_FG,
                alignment=1,
            ))]],
            colWidths=[content_w],
        )
        ban.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), _GREEN_BG),
                    ("BOX", (0, 0), (-1, -1), 0.8, _GREEN_FG),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
    story.append(ban)
    story.append(Spacer(1, 0.5 * cm))

    if linza_sel:
        ct_ids = {x["id"]: x["label"] for x in CONTENT_TYPES}
        ct_lbl = ct_ids.get(linza_sel.content_type_id, linza_sel.content_type_id)
        story.append(_p(f"Тип контента (Linza): {ct_lbl}", small))
        story.append(Spacer(1, 0.25 * cm))

    if dets:
        story.append(
            _p(
                "Статистика по разделам классификатора (по зафиксированным вердиктам)",
                ParagraphStyle("h", parent=styles["Normal"], fontName=fn_b, fontSize=10, spaceAfter=6),
            )
        )
        by_chapter = Counter(str(d.get("chapter") or "Прочее") for d in dets)
        ranked = by_chapter.most_common(14)
        stat_header: list[list[Any]] = [
            [
                Paragraph(escape("Раздел классификатора"), tbl_head_on_blue),
                Paragraph(escape("Записей в отчёте"), tbl_head_on_blue),
            ]
        ]
        stat_rows: list[list[Any]] = []
        for name, cnt in ranked:
            stat_rows.append(
                [
                    Paragraph(escape(name[:72]), small),
                    Paragraph(escape(str(cnt)), tbl_cell),
                ]
            )
        bar_tbl = Table(
            stat_header + stat_rows,
            colWidths=[content_w - 2.8 * cm, 2.8 * cm],
        )
        bar_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), _BLUE_HEAD),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                    ("GRID", (0, 0), (-1, -1), 0.2, colors.HexColor("#e2e8f0")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ]
            )
        )
        story.append(bar_tbl)
        story.append(Spacer(1, 0.55 * cm))

        story.append(
            _p(
                "Обнаруженные нарушения",
                ParagraphStyle("h2", parent=styles["Normal"], fontName=fn_b, fontSize=11, spaceAfter=8),
            )
        )
        det_header: list[list[Any]] = [
            [
                Paragraph(escape("Категория"), tbl_head_on_blue),
                Paragraph(escape("Вердикт"), tbl_head_on_blue),
                Paragraph(escape("Начало"), tbl_head_on_blue),
                Paragraph(escape("Конец"), tbl_head_on_blue),
                Paragraph(escape("Ув."), tbl_head_on_blue),
                Paragraph(escape("Источник"), tbl_head_on_blue),
            ]
        ]
        det_body: list[list[Any]] = []
        for x in dets[:120]:
            cat = str(x.get("category_label") or x.get("subclass") or "")[:55]
            sub = str(x.get("subclass") or "")
            src = "аудио" if x.get("type") == "audio" else "видео"
            det_body.append(
                [
                    Paragraph(escape(cat), tbl_cell),
                    Paragraph(escape(sub), tbl_cell),
                    Paragraph(escape(str(x.get("start_time", ""))), tbl_cell),
                    Paragraph(escape(str(x.get("end_time", ""))), tbl_cell),
                    Paragraph(escape(str(x.get("confidence", ""))), tbl_cell),
                    Paragraph(escape(src), tbl_cell),
                ]
            )
        dt = Table(
            det_header + det_body,
            colWidths=[
                4.6 * cm,
                2.2 * cm,
                2.2 * cm,
                2.2 * cm,
                1.5 * cm,
                max(1.0 * cm, content_w - (4.6 + 2.2 + 2.2 + 2.2 + 1.5) * cm),
            ],
        )
        dt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), _BLUE_HEAD),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fff1f2")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#fecdd3")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(dt)
        if len(dets) > 120:
            story.append(_p(f"… и ещё {len(dets) - 120} записей (полный список — в JSON export time-based).", small))

    story.append(PageBreak())
    story.append(
        _p(
            "Кадры с ненулевым вердиктом",
            ParagraphStyle("h3", parent=styles["Normal"], fontName=fn_b, fontSize=11, spaceAfter=8),
        )
    )
    flagged = [r for r in results if not _is_clean(_subclass_from_row(r))]
    if flagged:
        rh = [
            [
                Paragraph(escape("Сек"), tbl_head_on_blue),
                Paragraph(escape("Вердикт"), tbl_head_on_blue),
                Paragraph(escape("Пояснение"), tbl_head_on_blue),
            ]
        ]
        rb: list[list[Any]] = []
        for r in flagged[:100]:
            sub = _subclass_from_row(r)
            rule = linza_rule_by_verdict(sub)
            v_show = str(rule["title"]) if rule else sub
            rb.append(
                [
                    Paragraph(escape(str(r.get("time_sec", ""))), tbl_cell),
                    Paragraph(escape(v_show[:80]), tbl_cell),
                    _p(_reason_from_frame_row(r) or "—", small),
                ]
            )
        ft = Table(rh + rb, colWidths=[2 * cm, 4.5 * cm, max(4 * cm, content_w - 6.5 * cm)])
        ft.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), _BLUE_HEAD),
                    ("BACKGROUND", (0, 1), (-1, -1), _BLUE_SOFT),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c7d2fe")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(ft)
    else:
        story.append(_p("Нет кадров с вердиктом отличным от «none».", body))

    if audio and not (isinstance(audio.get("error"), str) and audio.get("error")):
        story.append(Spacer(1, 0.5 * cm))
        story.append(
            _p(
                "Речь: итог модерации",
                ParagraphStyle("h3b", parent=styles["Normal"], fontName=fn_b, fontSize=11, spaceAfter=6),
            )
        )
        mod = audio.get("moderation_parsed")
        if not isinstance(mod, dict):
            mod = None
        if mod:
            av = str(mod.get("verdict") or "").strip()
            ar = str(mod.get("reason") or "").strip()[:1200]
            story.append(_p(f"Вердикт: {av}", body))
            if ar:
                story.append(_p(f"Пояснение: {ar}", small))
        elif audio.get("moderation_note"):
            story.append(_p(str(audio.get("moderation_note")), small))
        else:
            story.append(_p("Модерация речи не выполнена или нет данных.", small))

    doc.build(story)
    return buf.getvalue()
