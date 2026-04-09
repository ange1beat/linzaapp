import os
import tempfile

# Set test DB path BEFORE importing the app (module-level engine creation)
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["ERROR_DB_PATH"] = _tmp.name

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import Base, app, engine  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db():
    """Drop and recreate all tables between tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    return TestClient(app)
