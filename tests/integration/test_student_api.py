"""Integration test IT-09: Submit Application (Student)."""

from sqlmodel import select

from app.models.application import Application
from app.models.student import Student
from tests.integration.conftest import application_body


def test_IT09_student_submits_application(client, db, student_headers):
    response = client.put("/api/application", json=application_body(), headers=student_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "submitted"
    student = db.exec(select(Student).where(Student.student_id == "816000001")).one()
    assert student.full_name == "Bob Smith"
    application = db.exec(select(Application).where(Application.student_id == student.id)).one()
    assert application.status == "submitted"
