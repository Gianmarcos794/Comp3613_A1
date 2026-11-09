"""Unit tests UT-11 to UT-14: MatchService (Match Application to Internship)."""

from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from app.models.application import Application
from app.models.internship import Internship
from app.models.student import Student
from app.services.match_service import MatchError, MatchService
from tests.unit.fakes import FakeApplicationRepo, FakeInternshipRepo, FakeMatchRepo, FakeStudentRepo


@pytest.fixture
def ctx():
    students, applications = FakeStudentRepo(), FakeApplicationRepo()
    internships, matches = FakeInternshipRepo(), FakeMatchRepo()

    student = students.save(Student(
        user_id=5, full_name="Bob Smith", student_id="816000001",
        program="Computer Science", year_of_study=3, gpa=3.5,
    ))
    application = applications.save(Application(student_id=student.id, status="submitted"))
    internship = internships.save(Internship(
        company_id=1, title="Backend Intern", description="FastAPI work", location="Remote",
        required_program="Computer Science", minimum_gpa=3.0, minimum_year=2,
        number_of_positions=2, deadline=date.today() + timedelta(days=30), status="open",
    ))
    internships.eligible = [(internship, SimpleNamespace(company_name="Acme"))]

    return SimpleNamespace(
        service=MatchService(applications, students, internships, matches),
        application=application,
        internship=internship,
        internships=internships,
    )


def test_UT11_match_creates_match_and_marks_application_matched(ctx):
    match, internship = ctx.service.match_application(ctx.application.id, ctx.internship.id)

    assert match.id is not None
    assert match.application_id == ctx.application.id
    assert ctx.application.status == "matched"
    assert internship.status == "open"  # 1 of 2 positions filled


def test_UT12_filling_last_position_closes_internship(ctx):
    ctx.internship.number_of_positions = 1

    _, internship = ctx.service.match_application(ctx.application.id, ctx.internship.id)

    assert internship.status == "closed"


def test_UT13_match_refuses_ineligible_internship(ctx):
    ctx.internships.eligible = []  # student no longer meets the requirements

    with pytest.raises(MatchError, match="isn't eligible"):
        ctx.service.match_application(ctx.application.id, ctx.internship.id)

    assert ctx.application.status == "submitted"


def test_UT14_reject_marks_application_rejected(ctx):
    student = ctx.service.reject_application(ctx.application.id)

    assert ctx.application.status == "rejected"
    assert student.full_name == "Bob Smith"
