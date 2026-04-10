import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./linza_board.db")

# SQLite needs check_same_thread=False; PostgreSQL does not support it.
_connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def run_sqlite_migrations():
    """Таблицы уже есть — добавляем колонки для SQLite без Alembic."""
    if not str(engine.url).startswith("sqlite"):
        return
    alters = [
        "ALTER TABLE yandex_oauth_states ADD COLUMN frontend_base VARCHAR(512)",
        "ALTER TABLE video_analysis_queue ADD COLUMN detector_job_id VARCHAR(128)",
        "ALTER TABLE video_analysis_queue ADD COLUMN report_id INTEGER",
        "ALTER TABLE video_analysis_queue ADD COLUMN error_message TEXT",
        "ALTER TABLE users ADD COLUMN portal_roles TEXT",
        "ALTER TABLE analysis_reports ADD COLUMN content_marking VARCHAR(32)",
        "ALTER TABLE analysis_reports ADD COLUMN revision_done BOOLEAN DEFAULT 0",
        "ALTER TABLE analysis_reports ADD COLUMN escalated BOOLEAN DEFAULT 0",
    ]
    for stmt in alters:
        try:
            with engine.begin() as conn:
                conn.execute(text(stmt))
        except Exception:
            pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Apply database schema.

    PostgreSQL → Alembic migrations (supports ALTER TABLE, versioned schema).
    SQLite     → Base.metadata.create_all() (simple, fast, used for dev/test).
    """
    if DATABASE_URL.startswith("postgresql"):
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
        )
        command.upgrade(alembic_cfg, "head")
    else:
        Base.metadata.create_all(bind=engine)
