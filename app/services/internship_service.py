from datetime import date

from app.models.company import Company
from app.models.internship import Internship
from app.models.user import User
from app.repositories.company import CompanyRepository
from app.repositories.internship import InternshipRepository
from app.repositories.match import MatchRepository
from app.schemas.internship import InternshipForm
from app.utilities.grading import GPA_MAX


class InternshipError(Exception):
    """A request the rules refuse; the message is safe to show the company."""


class InternshipService:
    def __init__(
        self,
        company_repo: CompanyRepository,
        internship_repo: InternshipRepository,
        match_repo: MatchRepository,
    ):
        self.company_repo = company_repo
        self.internship_repo = internship_repo
        self.match_repo = match_repo

    def get_company(self, user: User) -> Company:
        company = self.company_repo.get_by_user_id(user.id)
        if company is None:
            raise InternshipError("This login has no company profile.")
        return company

    def list_for_company(self, user: User) -> tuple[Company, list[Internship], dict[int, int]]:
        company = self.get_company(user)
        internships = self.internship_repo.get_by_company(company.id)
        match_counts = self.match_repo.counts_for_internships([i.id for i in internships])
        return company, internships, match_counts

    def get_owned(self, user: User, internship_id: int) -> Internship:
        company = self.get_company(user)
        internship = self.internship_repo.get_by_id(internship_id)
        if internship is None or internship.company_id != company.id:
            raise InternshipError("Internship not found.")
        return internship

    def _check_form(self, form: InternshipForm) -> None:
        if not 0 <= form.minimum_gpa <= GPA_MAX:
            raise InternshipError(f"Minimum GPA must be between 0 and {GPA_MAX}.")

    def create_internship(self, user: User, form: InternshipForm) -> Internship:
        company = self.get_company(user)
        self._check_form(form)
        if form.deadline < date.today():
            raise InternshipError("The deadline can't be in the past.")
        internship = Internship(company_id=company.id, status="open", **form.model_dump())
        return self.internship_repo.save(internship)

    def update_internship(self, user: User, internship_id: int, form: InternshipForm) -> Internship:
        internship = self.get_owned(user, internship_id)
        if internship.status == "closed":
            raise InternshipError("This internship is closed and can no longer be edited.")
        self._check_form(form)
        matched = self.match_repo.count_for_internship(internship.id)
        if form.number_of_positions < matched:
            raise InternshipError(
                f"{matched} student(s) are already matched, so positions can't go below {matched}."
            )
        for field, value in form.model_dump().items():
            setattr(internship, field, value)
        # Filling every position closes the internship (Phase 3 rule).
        if matched >= internship.number_of_positions:
            internship.status = "closed"
        return self.internship_repo.save(internship)

    def close_internship(self, user: User, internship_id: int) -> Internship:
        internship = self.get_owned(user, internship_id)
        if internship.status == "closed":
            raise InternshipError("This internship is already closed.")
        internship.status = "closed"
        return self.internship_repo.save(internship)

    def matched_students(self, user: User, internship_id: int):
        internship = self.get_owned(user, internship_id)
        return internship, self.match_repo.get_matched_students(internship.id)
