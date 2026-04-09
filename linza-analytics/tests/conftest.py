import pytest
from fastapi.testclient import TestClient

import app.config as config_module
from app.db import init_db
from app.main import app


@pytest.fixture(autouse=True)
def tmp_db(monkeypatch, tmp_path):
    """Override DATABASE_PATH with a temporary file so tests never touch the real DB."""
    db_path = str(tmp_path / "test_linza.db")
    monkeypatch.setattr(config_module, "DATABASE_PATH", db_path)
    init_db()
    yield db_path


@pytest.fixture()
def client():
    return TestClient(app, raise_server_exceptions=False)
