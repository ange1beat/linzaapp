"""Centralized configuration — all env vars in one place."""

import os

_DEFAULT_DB = os.path.join(os.path.dirname(__file__), "..", "data", "linza.db")

DATABASE_PATH: str = os.getenv("DATABASE_PATH", _DEFAULT_DB)
ERROR_TRACKER_URL: str = os.getenv("ERROR_TRACKER_URL", "http://localhost:8004")
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
