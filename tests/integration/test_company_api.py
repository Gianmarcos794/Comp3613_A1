"""Integration tests IT-05 to IT-08: Publish/Manage Internships (Company)."""

from datetime import date, timedelta

from sqlmodel import select

from app.models.internship import Internship
from tests.integration.conftest import create_company, internship_body


def test_IT05_company_publishes_internship(client, db, company, company_headers):
    response = client.post("/api/internships", json=internship_body(), headers=company_headers)

    assert response.status_code == 201
    assert response.json()["status"] == "open"
    saved = db.get(Internship, response.json()["id"])
    assert saved.company_id == company.id
    assert saved.title == "Backend Intern"


def test_IT06_past_deadline_is_refused(client, db, company_headers):
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    response = client.post(
        "/api/internships", json=internship_body(deadline=yesterday), headers=company_headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The deadline can't be in the past."
    assert db.exec(select(Internship)).all() == []


def test_IT07_cannot_view_another_companys_internship(client, db, company_headers):
    other = create_company(db, "globex")
    theirs = Internship(company_id=other.id, status="open", **{
        **internship_body(), "deadline": date.today() + timedelta(days=30),
    })
    db.add(theirs)
    db.commit()

    response = client.get(f"/api/internships/{theirs.id}", headers=company_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Internship not found."


def test_IT08_company_closes_internship(client, db, company_headers):
    created = client.post("/api/internships", json=internship_body(), headers=company_headers).json()

    response = client.patch(
        f"/api/internships/{created['id']}", json={"status": "closed"}, headers=company_headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "closed"
    assert db.get(Internship, created["id"]).status == "closed"
