#!/usr/bin/env python3
"""Локальный запуск из корня репозитория. В Docker предпочтительнее:

    python -m backend.slim_detector_reports [--dry-run]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.slim_detector_reports import main  # noqa: E402

if __name__ == "__main__":
    main()
