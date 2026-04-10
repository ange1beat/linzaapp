"""Helpers for exporting job results as JSON."""

from __future__ import annotations

import json
from typing import Any

from app.time_report import build_time_based_report


def infer_fps_from_results(results: list[dict[str, Any]]) -> float | None:
    pairs: list[tuple[float, float]] = []
    for r in results:
        if r.get("time_sec") is None or r.get("frame_index") is None:
            continue
        t, fi = float(r["time_sec"]), float(r["frame_index"])
        if t > 1e-3:
            pairs.append((t, fi))
    if len(pairs) < 2:
        return None
    pairs.sort(key=lambda x: x[0])
    t0, f0 = pairs[0]
    t1, f1 = pairs[-1]
    dt = t1 - t0
    if dt <= 1e-6:
        return None
    df = f1 - f0
    if df <= 0:
        return None
    v = df / dt
    if 1.0 <= v <= 120.0:
        return v
    return None


def effective_source_meta(
    row: dict[str, Any],
    results: list[dict[str, Any]],
) -> tuple[int | None, float | None]:
    fc = row.get("video_frame_count")
    fps_db = row.get("video_fps")
    fc_i = int(fc) if fc is not None and int(fc) > 0 else None
    fps_f = float(fps_db) if fps_db is not None and float(fps_db) > 0 else None
    fps = fps_f or infer_fps_from_results(results)

    max_fi = 0
    for r in results:
        if r.get("frame_index") is not None:
            max_fi = max(max_fi, int(r["frame_index"]))

    if fc_i:
        return fc_i, fps

    if fps and fps > 0 and results:
        last_t = max(float(r.get("time_sec", 0)) for r in results)
        est = max(int(round(last_t * fps)) + 1, max_fi + 1)
        return est, fps

    if max_fi >= 0:
        return max_fi + 1, fps
    return None, fps


def parse_audio_results(row: dict[str, Any]) -> dict[str, Any] | None:
    raw = row.get("audio_results_json")
    if not raw:
        return None
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def build_time_based_export(
    row: dict[str, Any],
    results: list[dict[str, Any]],
    *,
    job_id: str,
) -> dict[str, Any]:
    fc, fps = effective_source_meta(row, results)
    audio = parse_audio_results(row)
    report = build_time_based_report(
        results,
        frame_count=fc,
        fps=fps,
        job_id=job_id,
        audio=audio,
    )
    if audio:
        report["audio"] = audio
    return report


def build_raw_export(
    job_id: str,
    results: list[dict[str, Any]],
    *,
    row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "export_type": "RAW_FRAME_RESULTS",
        "job_id": job_id,
        "results": results,
    }
    if row:
        audio = parse_audio_results(row)
        if audio:
            out["audio"] = audio
    return out


def parse_results_json(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw = row.get("results_json")
    if not raw:
        return []
    data = json.loads(raw) if isinstance(raw, str) else raw
    return data if isinstance(data, list) else []
