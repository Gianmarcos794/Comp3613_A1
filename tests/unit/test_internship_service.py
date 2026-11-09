"""Unit tests UT-01 to UT-07: InternshipService (Publish/Manage Internships)."""

from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from app.models.company import Company
from app.models.internship import Internship
from app.schemas.internship import InternshipForm
from app.services.internship_service import InternshipError, InternshipService
from tests.unit.fakes import FakeCompanyRepo, FakeInternshipRepo, FakeMatchRepo


def make_form(**overrides) -> InternshipForm:
    data = dict(
        title="Backend Intern", description="FastAPI work", location="Port of Spain",
        required_program="Computer Science", minimum_gpa=3.0, minimum_year=2,
        number_of_positions=2, deadline=date.today() + timedelta(days=30),
    )
    data.update(overrides)
    return InternshipForm(**data)


@pytest.fixture
def ctx():
    companies = FakeCompanyRepo()
    companies.save(Company(user_id=1, company_name="Acme", contact_email="hr@acme.com", industry="Tech"))
    internships, matches = FakeInternshipRepo(), FakeMatchRepo()
    return SimpleNamespace(
        service=InternshipService(companies, internships, matches),
        user=SimpleNamespace(id=1),
        company_id=1,
        internships=internships,
        matches=matches,
    )


def test_UT01_create_internship_saves_as_open(ctx):
    internship = ctx.service.create_internship(ctx.user, make_form())

    assert internship.id is not None
    assert internship.company_id == ctx.company_id
    assert internship.status == "open"


def test_UT02_create_internship_rejects_past_deadline(ctx):
    with pytest.raises(InternshipError, match="deadline can't be in the past"):
        ctx.service.create_internship(ctx.user, make_form(deadline=date.today() - timedelta(days=1)))


def test_UT03_get_owned_hides_another_companys_internship(ctx):
    other = ctx.internships.save(Internship(company_id=99, status="open", **make_form().model_dump()))

    with pytest.raises(InternshipError, match="Internship not found"):
        ctx.service.get_owned(ctx.user, other.id)


def test_UT04_update_refuses_closed_internship(ctx):
    internship = ctx.service.create_internship(ctx.user, make_form())
    internship.status = "closed"

    with pytest.raises(InternshipError, match="closed and can no longer be edited"):
        ctx.service.update_internship(ctx.user, internship.id, make_form(title="New title"))


def test_UT05_update_positions_cannot_drop_below_matched(ctx):
    internship = ctx.service.create_internship(ctx.user, make_form(number_of_positions=3))
    ctx.matches.counts[internship.id] = 2

    with pytest.raises(InternshipError, match="can't go below 2"):
        ctx.service.update_internship(ctx.user, internship.id, make_form(number_of_positions=1))


def test_UT06_filling_all_positions_closes_internship(ctx):
    internship = ctx.service.create_internship(ctx.user, make_form(number_of_positions=3))
    ctx.matches.counts[internship.id] = 2

    updated = ctx.service.update_internship(ctx.user, internship.id, make_form(number_of_positions=2))

    assert updated.status == "closed"


def test_UT07_close_refuses_already_closed(ctx):
    internship = ctx.service.create_internship(ctx.user, make_form())
    ctx.service.close_internship(ctx.user, internship.id)

    with pytest.raises(InternshipError, match="already closed"):
        ctx.service.close_internship(ctx.user, internship.id)
