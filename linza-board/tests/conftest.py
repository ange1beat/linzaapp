import os

# Override DATABASE_URL before any app imports
os.environ["DATABASE_URL"] = "sqlite:///./test_linza_board.db"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.database import Base, get_db
from backend.main import app
from backend.auth import hash_password, seed_superadmin
from backend.models import User

TEST_DATABASE_URL = "sqlite:///./test_linza_board.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them after.

    Also resets the rate limiter between tests to avoid cross-test
    interference from the in-memory storage.
    """
    from backend.rate_limit import limiter
    limiter.reset()

    Base.metadata.create_all(bind=engine)
    # Seed the superadmin
    db = TestingSessionLocal()
    try:
        seed_superadmin(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def admin_token(client):
    """Get a JWT token for the default superadmin user."""
    response = client.post("/api/auth/login", json={
        "login": "admin",
        "password": "admin",
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token):
    """Return Authorization headers for the superadmin."""
    return {"Authorization": f"Bearer {admin_token}"}
