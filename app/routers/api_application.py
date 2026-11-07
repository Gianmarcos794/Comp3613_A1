"""JSON API: Submit Application / View Application Status (Student)."""

from fastapi import HTTPException, status

from app.dependencies import SessionDep, StudentDep
from app.repositories.application import ApplicationRepository
from app.repositories.match import MatchRepository
from app.repositories.student import StudentRepository
from app.schemas.application import ApplicationForm
from app.services.application_service import ApplicationError, ApplicationService
from . import api_router
from .api_auth import api_error


def _service(db) -> ApplicationService:
    return ApplicationService(StudentRepository(db), ApplicationRepository(db), MatchRepository(db))


@api_router.get("/application")
def api_get_application(user: StudentDep, db: SessionDep):
    service = _service(db)
    student, application = service.get_for_user(user)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You have not submitted an application yet.")
    placement = service.get_placement(application)
    return {
        "student": student,
        "application": application,
        "placement": None if placement is None else {
            "internship": placement[1],
            "company_name": placement[2].company_name,
        },
    }


# PUT: each student has exactly one application, so submit and resubmit both replace it.
@api_router.put("/application")
def api_submit_application(body: ApplicationForm, user: StudentDep, db: SessionDep):
    try:
        return _service(db).submit_application(user, body)
    except ApplicationError as e:
        raise api_error(e)
