"""Integration tests IT-10 and IT-11: Match Application to Internship (Admin)."""

from sqlmodel import select

from app.models.application import Application
from app.models.company import Company
from app.models.internship import Internship
from app.models.match import Match
from app.models.user import User
from tests.integration.conftest import application_body, internship_body


def test_IT10_admin_creates_company_account(client, db, admin_headers):
    response = client.post("/api/companies", headers=admin_headers, json={
        "username": "initech", "email": "login@initech.com", "password": "initechpass",
        "company_name": "Initech", "contact_email": "hr@initech.com", "industry": "Software",
    })

    assert response.status_code == 201
    assert response.json()["company_name"] == "Initech"
    user = db.exec(select(User).where(User.username == "initech")).one()
    assert user.role == "company"
    assert db.exec(select(Company).where(Company.user_id == user.id)).one().industry == "Software"


def test_IT11_admin_matches_application_and_fills_last_position(
    client, db, admin_headers, company_headers, student_headers
):
    internship = client.post(
        "/api/internships", json=internship_body(number_of_positions=1), headers=company_headers
    ).json()
    application = client.put("/api/application", json=application_body(), headers=student_headers).json()

    response = client.post(
        "/api/matches",
        json={"application_id": application["id"], "internship_id": internship["id"]},
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["internship"]["status"] == "closed"
    match = db.exec(select(Match)).one()
    assert match.application_id == application["id"]
    assert db.get(Application, application["id"]).status == "matched"
    assert db.get(Internship, internship["id"]).status == "closed"
