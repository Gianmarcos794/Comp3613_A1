"""Integration tests IT-01 to IT-04: authentication and authorization."""

from sqlmodel import select

from app.models.internship import Internship
from app.models.user import User
from tests.integration.conftest import create_user, internship_body


def test_IT01_register_creates_student(client, db):
    response = client.post(
        "/api/register",
        json={"username": "alice", "email": "alice@uwi.edu", "password": "alicepass"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "student"
    user = db.exec(select(User).where(User.username == "alice")).one()
    assert user.role == "student"


def test_IT02_login_with_wrong_password_is_refused(client, db):
    create_user(db, "bob", "student")

    response = client.post("/api/login", json={"username": "bob", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_IT03_no_token_is_unauthorized(client):
    response = client.get("/api/internships")

    assert response.status_code == 401
    assert "detail" in response.json()


def test_IT04_student_cannot_publish_internship(client, db, student_headers):
    response = client.post("/api/internships", json=internship_body(), headers=student_headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Only companies can access this page"
    assert db.exec(select(Internship)).all() == []
