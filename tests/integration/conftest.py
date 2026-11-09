"""Shared setup for integration tests.

Every test gets a brand-new in-memory SQLite database. The app's session
dependency is overridden so requests made with TestClient run through the real
routes, services and repositories against that test database, never the real one.
"""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  (registers every table on SQLModel.metadata)
from app.database import get_session
from app.main import app as fastapi_app
from app.models.company import Company
from app.models.user import User
from app.utilities.security import encrypt_password

PASSWORD = "testpass"


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine):
    """A session the test uses to set up rows and check the database afterwards."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(engine):
    def test_session():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = test_session
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()


# ── Helpers ──────────────────────────────────────────────────────────────

def create_user(db, username: str, role: str) -> User:
    user = User(
        username=username, email=f"{username}@uni.edu",
        password=encrypt_password(PASSWORD), role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_company(db, username: str) -> Company:
    user = create_user(db, username, "company")
    company = Company(
        user_id=user.id, company_name=username.title(),
        contact_email=f"hr@{username}.com", industry="Tech",
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def login(client, username: str, password: str = PASSWORD) -> dict:
    response = client.post("/api/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def internship_body(**overrides) -> dict:
    body = dict(
        title="Backend Intern", description="FastAPI work", location="Port of Spain",
        required_program="Computer Science", minimum_gpa=3.0, minimum_year=2,
        number_of_positions=2, deadline=(date.today() + timedelta(days=30)).isoformat(),
    )
    body.update(overrides)
    return body


def application_body(**overrides) -> dict:
    body = dict(
        full_name="Bob Smith", student_id="816000001", program="Computer Science",
        year_of_study=3, gpa=3.5, projects="Chess engine", preferences="Backend",
    )
    body.update(overrides)
    return body


# ── Logged-in users ──────────────────────────────────────────────────────

@pytest.fixture
def admin_headers(client, db):
    create_user(db, "admin", "admin")
    return login(client, "admin")


@pytest.fixture
def company(db):
    return create_company(db, "acme")


@pytest.fixture
def company_headers(client, company):
    return login(client, "acme")


@pytest.fixture
def student_headers(client, db):
    create_user(db, "bob", "student")
    return login(client, "bob")
