from datetime import date

from app.models.application import Application
from app.models.company import Company
from app.models.internship import Internship
from app.models.match import Match
from app.models.student import Student
from app.repositories.application import ApplicationRepository
from app.repositories.internship import InternshipRepository
from app.repositories.match import MatchRepository
from app.repositories.student import StudentRepository


class MatchError(Exception):
    """A request the rules refuse; the message is safe to show the Admin."""


class MatchService:
    def __init__(
        self,
        application_repo: ApplicationRepository,
        student_repo: StudentRepository,
        internship_repo: InternshipRepository,
        match_repo: MatchRepository,
    ):
        self.application_repo = application_repo
        self.student_repo = student_repo
        self.internship_repo = internship_repo
        self.match_repo = match_repo

    # —— Admin dashboard ——
    def list_applications(self, query: str = "", unmatched_only: bool = True) -> list[tuple[Application, Student]]:
        return self.application_repo.search_with_students(query.strip(), "submitted" if unmatched_only else None)

    def placements_for(self, application_ids: list[int]) -> dict[int, tuple[Internship, Company]]:
        return self.match_repo.get_placements(application_ids)

    def list_internships(self) -> tuple[list[tuple[Internship, Company]], dict[int, int]]:
        rows = self.internship_repo.get_all_with_company()
        counts = self.match_repo.counts_for_internships([i.id for i, _ in rows])
        return rows, counts

    # —— Match Application ——
    def get_application(self, application_id: int) -> tuple[Application, Student]:
        application = self.application_repo.get_by_id(application_id)
        if application is None:
            raise MatchError("Application not found.")
        student = self.student_repo.get_by_id(application.student_id)
        return application, student

    def eligible_internships(self, student: Student) -> list[tuple[Internship, Company]]:
        """Check Requirements: open, program matches, GPA and year meet the minimums, deadline not passed."""
        return self.internship_repo.find_matching(
            program=student.program,
            gpa=student.gpa,
            year=student.year_of_study,
            status="open",
            deadline_from=date.today(),
        )

    def match_application(self, application_id: int, internship_id: int) -> tuple[Match, Internship]:
        application, student = self.get_application(application_id)
        if application.status != "submitted":
            raise MatchError(f"This application is already {application.status}.")

        eligible = {internship.id: internship for internship, _ in self.eligible_internships(student)}
        internship = eligible.get(internship_id)
        if internship is None:
            raise MatchError("That internship isn't eligible for this student any more.")

        matched = self.match_repo.count_for_internship(internship.id)
        if matched >= internship.number_of_positions:
            raise MatchError("That internship has no positions left.")

        application.status = "matched"
        # Filling the last position closes the internship (Phase 3 rule).
        if matched + 1 >= internship.number_of_positions:
            internship.status = "closed"
        match = self.match_repo.create_match(
            Match(application_id=application.id, internship_id=internship.id),
            application,
            internship,
        )
        return match, internship

    def reject_application(self, application_id: int) -> Student:
        application, student = self.get_application(application_id)
        if application.status != "submitted":
            raise MatchError(f"This application is already {application.status}.")
        application.status = "rejected"
        self.application_repo.save(application)
        return student
