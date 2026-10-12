from app.models.company import Company
from app.repositories.company import CompanyRepository
from app.repositories.user import UserRepository
from app.schemas.company import CompanyAccountForm
from app.schemas.user import CompanyUserCreate
from app.utilities.security import encrypt_password


class CompanyError(Exception):
    """A request the rules refuse; the message is safe to show the Admin."""


class CompanyService:
    def __init__(self, user_repo: UserRepository, company_repo: CompanyRepository):
        self.user_repo = user_repo
        self.company_repo = company_repo

    def list_companies(self) -> list[Company]:
        return self.company_repo.get_all()

    def create_company_account(self, form: CompanyAccountForm) -> Company:
        if self.user_repo.get_by_username(form.username):
            raise CompanyError("That username is already taken.")
        if self.user_repo.get_by_email(form.email):
            raise CompanyError("That login email is already in use.")

        user = self.user_repo.create(
            CompanyUserCreate(
                username=form.username,
                email=form.email,
                password=encrypt_password(form.password),
            )
        )
        try:
            return self.company_repo.save(
                Company(
                    user_id=user.id,
                    company_name=form.company_name,
                    contact_email=form.contact_email,
                    industry=form.industry,
                )
            )
        except Exception:
            # Don't leave a company login with no COMPANY profile behind.
            self.user_repo.delete_user(user.id)
            raise
