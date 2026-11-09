"""Unit tests UT-08 to UT-10: ApplicationService (Submit Application)."""

from types import SimpleNamespace

import pytest

from app.schemas.application import ApplicationForm
from app.services.application_service import ApplicationError, ApplicationService
from tests.unit.fakes import FakeApplicationRepo, FakeStudentRepo


def make_form(**overrides) -> ApplicationForm:
    data = dict(
        full_name="Bob Smith", student_id="816000001", program="Computer Science",
        year_of_study=3, gpa=3.5, projects="Chess engine", preferences="Backend",
    )
    data.update(overrides)
    return ApplicationForm(**data)


@pytest.fixture
def ctx():
    students, applications = FakeStudentRepo(), FakeApplicationRepo()
    return SimpleNamespace(
        service=ApplicationService(students, applications),
        user=SimpleNamespace(id=5),
        students=students,
        applications=applications,
    )


def test_UT08_first_submit_creates_profile_and_application(ctx):
    application = ctx.service.submit_application(ctx.user, make_form())

    student = ctx.students.get_by_user_id(ctx.user.id)
    assert student is not None
    assert student.full_name == "Bob Smith"
    assert application.student_id == student.id
    assert application.status == "submitted"


def test_UT09_matched_application_cannot_be_changed(ctx):
    application = ctx.service.submit_application(ctx.user, make_form())
    application.status = "matched"

    with pytest.raises(ApplicationError, match="has been matched"):
        ctx.service.submit_application(ctx.user, make_form(preferences="Frontend"))


def test_UT10_gpa_above_cap_is_refused(ctx):
    with pytest.raises(ApplicationError, match="GPA must be between 0 and 4.3"):
        ctx.service.submit_application(ctx.user, make_form(gpa=4.5))

    assert ctx.applications.rows == {}
