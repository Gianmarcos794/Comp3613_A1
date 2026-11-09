"""Unit tests UT-15 and UT-16: AuthService and CompanyService (accounts)."""

import pytest

from app.models.user import User
from app.schemas.company import CompanyAccountForm
from app.services.auth_service import AuthService, RegistrationError
from app.services.company_service import CompanyError, CompanyService
from tests.unit.fakes import FakeCompanyRepo, FakeUserRepo


def test_UT15_register_refuses_non_university_email():
    users = FakeUserRepo()

    with pytest.raises(RegistrationError, match="university email"):
        AuthService(users).register_user("bob", "bob@gmail.com", "bobpass")

    assert users.rows == {}


def test_UT16_create_company_refuses_taken_username():
    users = FakeUserRepo()
    users.save(User(username="acme", email="old@acme.com", password="x", role="company"))
    companies = FakeCompanyRepo()
    form = CompanyAccountForm(
        username="acme", email="hr@acme.com", password="acmepass",
        company_name="Acme", contact_email="contact@acme.com", industry="Tech",
    )

    with pytest.raises(CompanyError, match="username is already taken"):
        CompanyService(users, companies).create_company_account(form)

    assert companies.rows == {}
