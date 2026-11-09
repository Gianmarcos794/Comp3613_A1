"""Integration test IT-12: the full workflow across Admin, Company and Student."""

from tests.integration.conftest import application_body, internship_body, login


def test_IT12_end_to_end_match_workflow(client, admin_headers):
    # Admin creates the company's account
    created = client.post("/api/companies", headers=admin_headers, json={
        "username": "initech", "email": "login@initech.com", "password": "initechpass",
        "company_name": "Initech", "contact_email": "hr@initech.com", "industry": "Software",
    })
    assert created.status_code == 201

    # Company logs in and publishes an internship
    company_headers = login(client, "initech", "initechpass")
    internship = client.post("/api/internships", json=internship_body(), headers=company_headers)
    assert internship.status_code == 201
    internship_id = internship.json()["id"]

    # Student registers, logs in and applies
    registered = client.post(
        "/api/register", json={"username": "alice", "email": "alice@uwi.edu", "password": "alicepass"}
    )
    assert registered.status_code == 201
    student_headers = login(client, "alice", "alicepass")
    application = client.put(
        "/api/application", json=application_body(full_name="Alice Jones"), headers=student_headers
    )
    assert application.status_code == 200
    application_id = application.json()["id"]

    # Admin sees the internship as eligible and makes the match
    detail = client.get(f"/api/applications/{application_id}", headers=admin_headers).json()
    assert [i["id"] for i in detail["eligible_internships"]] == [internship_id]
    matched = client.post(
        "/api/matches",
        json={"application_id": application_id, "internship_id": internship_id},
        headers=admin_headers,
    )
    assert matched.status_code == 201

    # Student sees the placement
    status = client.get("/api/application", headers=student_headers).json()
    assert status["application"]["status"] == "matched"
    assert status["placement"]["company_name"] == "Initech"
    assert status["placement"]["internship"]["id"] == internship_id

    # Company sees the matched student
    matches = client.get(f"/api/internships/{internship_id}/matches", headers=company_headers).json()
    assert [m["student"]["full_name"] for m in matches] == ["Alice Jones"]
