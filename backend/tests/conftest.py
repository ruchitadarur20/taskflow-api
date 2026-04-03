"""
Shared pytest fixtures.

Uses an in-memory SQLite database so tests run without a live Postgres instance.
"""
import os
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=False)
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helpers ───────────────────────────────────────────────────────────────────

def create_role(db, name: str = "member"):
    from app.models.role import Role
    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        return existing
    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def register_user(client, email: str = "test@example.com",
                  password: str = "password123", full_name: str = "Test User"):
    return client.post(
        "/auth/register",
        params={"full_name": full_name, "email": email, "password": password},
    )


def login_user(client, email: str = "test@example.com", password: str = "password123"):
    resp = client.post("/auth/login", data={"username": email, "password": password})
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(client, db):
    create_role(db, "member")
    register_user(client)
    token = login_user(client)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(client, db):
    create_role(db, "member")
    register_user(client, email="other@example.com", full_name="Other User")
    token = login_user(client, email="other@example.com")
    return {"Authorization": f"Bearer {token}"}
