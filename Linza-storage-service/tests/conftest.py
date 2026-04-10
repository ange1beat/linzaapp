import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.tasks import init_task_store, clear_tasks


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def task_store(tmp_path):
    """Provide a fresh SQLite-backed task store for every test."""
    os.environ["TASK_DB_PATH"] = str(tmp_path / "test_tasks.db")
    init_task_store()
    yield
    clear_tasks()
