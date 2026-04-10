"""Export job results as TIME_BASED_REPORT JSON (time-based detections)."""

from __future__ import annotations

import json
import math
from typing import Any

from app.linza_taxonomy import linza_rule_by_verdict


def _fmt_hms_total_seconds(total_sec: int) -> str:
    total_sec = max(0, int(total_sec))
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _interval_hms(start_sec: float, end_sec: float) -> tuple[str, str]:
    """Floor start, ceil end so short spans (e.g. 0–0.5s) show as 00:00:00 – 00:00:01."""
    a = max(0.0, float(start_sec))
    b = max(a, float(end_sec))
    lo = math.floor(a)
    hi = math.ceil(b)
    if hi < lo:
        hi = lo
    return _fmt_hms_total_seconds(lo), _fmt_hms_total_seconds(hi)


def _subclass_from_row(row: dict[str, Any]) -> str:
    p = row.get("verdict_parsed")
    if isinstance(p, dict):
        v = p.get("verdict")
        if v is not None:
            return str(v).strip().lower()
        if "allowed" in p:
            return "none" if p.get("allowed") else "flagged"
    raw = row.get("verdict_raw")
    if isinstance(raw, str) and raw.strip().startswith("{"):
        try:
            j = json.loads(raw)
            if isinstance(j, dict) and j.get("verdict") is not None:
                return str(j["verdict"]).strip().lower()
        except json.JSONDecodeError:
            pass
    return "unknown"


def _confidence_from_row(row: dict[str, Any]) -> float:
    p = row.get("verdict_parsed")
    if isinstance(p, dict):
        c = p.get("confidence")
        if isinstance(c, (int, float)):
            return float(c)
    return 1.0


def _reason_from_row(row: dict[str, Any]) -> str:
    p = row.get("verdict_parsed")
    if isinstance(p, dict) and p.get("reason") is not None:
        return str(p.get("reason", "")).strip()
    raw = row.get("verdict_raw")
    if isinstance(raw, str) and raw.strip().startswith("{"):
        try:
            j = json.loads(raw)
            if isinstance(j, dict) and j.get("reason") is not None:
                return str(j.get("reason", "")).strip()
        except json.JSONDecodeError:
            pass
    return ""


def _is_clean(subclass: str) -> bool:
    if subclass == "unknown":
        return True
    return subclass in ("", "none", "null", "ok", "clean")


def _moderation_dict_from_audio(audio: dict[str, Any]) -> dict[str, Any] | None:
    p = audio.get("moderation_parsed")
    if isinstance(p, dict):
        return p
    raw = audio.get("moderation_raw")
    if isinstance(raw, str) and raw.strip().startswith("{"):
        try:
            j = json.loads(raw)
            return j if isinstance(j, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _audio_moderation_detections(audio: dict[str, Any]) -> list[dict[str, Any]]:
    """Интервалы из модерации речи (spans) или одна запись на всю дорожку."""
    if audio.get("error") or audio.get("moderation_error"):
        return []
    mod = _moderation_dict_from_audio(audio)
    if not mod:
        return []
    verdict = str(mod.get("verdict") or "").strip().lower()
    if _is_clean(verdict):
        return []
    reason = str(mod.get("reason") or "").strip()
    conf = mod.get("confidence")
    conf_f = float(conf) if isinstance(conf, (int, float)) else 1.0
    rule = linza_rule_by_verdict(verdict)
    category_label = str(rule["title"]) if rule else verdict
    chapter = str(rule["chapter_title"]) if rule else "Речь (аудио)"

    spans = mod.get("spans")
    rows: list[dict[str, Any]] = []
    if isinstance(spans, list) and spans:
        for sp in spans:
            if not isinstance(sp, dict):
                continue
            try:
                start_sec = float(sp.get("start", 0))
            except (TypeError, ValueError):
                start_sec = 0.0
            try:
                end_sec = float(sp.get("end", start_sec))
            except (TypeError, ValueError):
                end_sec = start_sec
            st, et = _interval_hms(start_sec, end_sec)
            quote = str(sp.get("quote") or sp.get("text") or "").strip()
            rows.append(
                {
                    "startFrame": -1,
                    "endFrame": -1,
                    "subclass": verdict,
                    "confidence": round(conf_f, 6),
                    "type": "audio",
                    "start_time": st,
                    "end_time": et,
                    "time_interval": f"{st} – {et}",
                    "reason": reason,
                    "category_label": category_label,
                    "chapter": chapter,
                    "quote": quote[:500],
                }
            )
        return rows

    dur = audio.get("duration")
    if isinstance(dur, (int, float)) and float(dur) > 0:
        st, et = _interval_hms(0.0, float(dur))
    else:
        st = et = "00:00:00"
    return [
        {
            "startFrame": -1,
            "endFrame": -1,
            "subclass": verdict,
            "confidence": round(conf_f, 6),
            "type": "audio",
            "start_time": st,
            "end_time": et,
            "time_interval": f"{st} – {et}",
            "reason": reason,
            "category_label": category_label,
            "chapter": chapter,
            "quote": "",
        }
    ]


def _hms_to_sort_key(hms: str) -> tuple[int, int, int]:
    parts = (hms or "00:00:00").replace("–", "-").split("-")[0].strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        pass
    return 0, 0, 0


def build_time_based_report(
    results: list[dict[str, Any]],
    *,
    frame_count: int | None,
    fps: float | None,
    job_id: str | None = None,
    audio: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge consecutive samples with the same non-clean verdict into frame intervals."""
    rows = sorted(
        [r for r in results if "frame_index" in r],
        key=lambda x: int(x["frame_index"]),
    )
    detections: list[dict[str, Any]] = []
    i = 0
    eff_fps = fps if fps and fps > 0 else None

    while i < len(rows):
        sub = _subclass_from_row(rows[i])
        if _is_clean(sub):
            i += 1
            continue

        start_idx = int(rows[i]["frame_index"])
        end_idx = start_idx
        conf = _confidence_from_row(rows[i])
        j = i + 1
        while j < len(rows):
            sub2 = _subclass_from_row(rows[j])
            if sub2 == sub and not _is_clean(sub2):
                end_idx = int(rows[j]["frame_index"])
                conf = max(conf, _confidence_from_row(rows[j]))
                j += 1
            else:
                break

        start_sec = float(rows[i].get("time_sec", start_idx / eff_fps if eff_fps else 0))
        end_sec = float(rows[j - 1].get("time_sec", end_idx / eff_fps if eff_fps else start_sec))
        if eff_fps:
            start_sec = min(start_sec, start_idx / eff_fps)
            end_sec = max(end_sec, end_idx / eff_fps)

        st, et = _interval_hms(start_sec, end_sec)
        reason_v = _reason_from_row(rows[i])
        rule_v = linza_rule_by_verdict(sub)
        cat_v = str(rule_v["title"]) if rule_v else sub
        chap_v = str(rule_v["chapter_title"]) if rule_v else "Видео (кадры)"
        detections.append(
            {
                "startFrame": start_idx,
                "endFrame": end_idx,
                "subclass": sub,
                "confidence": round(conf, 6),
                "type": "video",
                "start_time": st,
                "end_time": et,
                "time_interval": f"{st} – {et}",
                "reason": reason_v[:2000] if reason_v else "",
                "category_label": cat_v,
                "chapter": chap_v,
            }
        )
        i = j

    if audio:
        detections.extend(_audio_moderation_detections(audio))

    detections.sort(key=lambda d: (_hms_to_sort_key(str(d.get("start_time", ""))), d.get("type", "")))

    out: dict[str, Any] = {
        "report_type": "TIME_BASED_REPORT",
        "source_info": {
            "frameCount": int(frame_count) if frame_count and frame_count > 0 else 0,
            "fps": float(fps) if fps and fps > 0 else 0.0,
        },
        "detections": detections,
    }
    if job_id:
        out["job_id"] = job_id
    return out
