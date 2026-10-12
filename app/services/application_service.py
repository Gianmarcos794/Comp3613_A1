from datetime import datetime, timezone
from typing import Optional, Tuple

from app.models.application import Application
from app.models.student import Student
from app.models.user import User
from app.repositories.application import ApplicationRepository
from app.repositories.match import MatchRepository
from app.repositories.student import StudentRepository
from app.schemas.application import ApplicationForm
from app.utilities.grading import GPA_MAX


class ApplicationError(Exception):
    """A submission the rules refuse; the message is safe to show the student."""


class ApplicationService:
    def __init__(
        self,
        student_repo: StudentRepository,
        application_repo: ApplicationRepository,
        match_repo: Optional[MatchRepository] = None,
    ):
        self.student_repo = student_repo
        self.application_repo = application_repo
        self.match_repo = match_repo

    def get_placement(self, application: Optional[Application]):
        """Matched internship + company for View Application Status, or None."""
        if application is None or application.status != "matched" or self.match_repo is None:
            return None
        return self.match_repo.get_placement(application.id)

    def get_for_user(self, user: User) -> Tuple[Optional[Student], Optional[Application]]:
        student = self.student_repo.get_by_user_id(user.id)
        application = self.application_repo.get_by_student(student.id) if student else None
        return student, application

    def submit_application(self, user: User, form: ApplicationForm) -> Application:
        student, application = self.get_for_user(user)

        if application and application.status == "matched":
            raise ApplicationError("Your application has been matched and can no longer be changed.")

        if not 0 <= form.gpa <= GPA_MAX:
            raise ApplicationError(f"GPA must be between 0 and {GPA_MAX}.")

        owner = self.student_repo.get_by_student_number(form.student_id)
        if owner and (student is None or owner.id != student.id):
            raise ApplicationError("That student ID is already used by another account.")

        # First submit creates the STUDENT profile; Edit / Resubmit updates it.
        if student is None:
            student = Student(user_id=user.id)
        student.full_name = form.full_name
        student.student_id = form.student_id
        student.program = form.program
        student.year_of_study = form.year_of_study
        student.gpa = form.gpa
        student = self.student_repo.save(student)

        # Edit / Resubmit goes back to the Admin's unmatched list as "submitted".
        if application is None:
            application = Application(student_id=student.id)
        application.projects = form.projects
        application.preferences = form.preferences
        application.status = "submitted"
        application.submitted_date = datetime.now(timezone.utc)
        return self.application_repo.save(application)
