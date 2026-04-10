"""Обрезка гигантского statusMessage в analysis_reports.report_json.

Запуск в контейнере (WORKDIR /app):

    python -m backend.slim_detector_reports --dry-run
    python -m backend.slim_detector_reports

Локально из корня репозитория linza-board:

    python -m backend.slim_detector_reports --dry-run
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")
load_dotenv()

from backend.database import SessionLocal
from backend.detector_service import _slim_job_payload
from backend.models import AnalysisReport


def main() -> None:
    ap = argparse.ArgumentParser(description="Slim bloated detector report_json in DB")
    ap.add_argument("--dry-run", action="store_true", help="Не писать в БД")
    ap.add_argument(
        "--min-status-message",
        type=int,
        default=501,
        help="Трогать только если len(statusMessage) >= этого порога",
    )
    args = ap.parse_args()

    db = SessionLocal()
    would_change = 0
    skipped = 0
    batch = 0
    try:
        rows = db.query(AnalysisReport).filter(AnalysisReport.report_json.isnot(None)).all()
        for r in rows:
            raw_s = (r.report_json or "").strip()
            if not raw_s:
                skipped += 1
                continue
            try:
                obj = json.loads(raw_s)
            except json.JSONDecodeError:
                skipped += 1
                continue
            if not isinstance(obj, dict):
                skipped += 1
                continue
            sm = obj.get("statusMessage")
            if not isinstance(sm, str) or len(sm) < args.min_status_message:
                skipped += 1
                continue
            slim = _slim_job_payload(obj)
            new_s = json.dumps(slim, ensure_ascii=False)
            if new_s == raw_s:
                skipped += 1
                continue
            old_len = len(raw_s)
            new_len = len(new_s)
            would_change += 1
            print(f"id={r.id} report_json {old_len} -> {new_len} bytes ({100 * new_len / old_len:.1f}%)")
            if not args.dry_run:
                r.report_json = new_s
                batch += 1
                if batch >= 50:
                    db.commit()
                    batch = 0
        if not args.dry_run and batch:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    verb = "Would slim" if args.dry_run else "Slimmed"
    print(f"{verb}: {would_change}, skipped: {skipped}")


if __name__ == "__main__":
    main()
