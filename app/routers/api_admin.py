"""JSON API: Match Application to Internship and Create Company Account (Admin)."""

from fastapi import status

from app.dependencies import AdminDep, SessionDep
from app.repositories.application import ApplicationRepository
from app.repositories.company import CompanyRepository
from app.repositories.internship import InternshipRepository
from app.repositories.match import MatchRepository
from app.repositories.student import StudentRepository
from app.repositories.user import UserRepository
from app.schemas.application import ApplicationStatusUpdate, MatchCreate
from app.schemas.company import CompanyAccountForm
from app.services.company_service import CompanyError, CompanyService
from app.services.match_service import MatchError, MatchService
from . import api_router
from .api_auth import api_error


def _match_service(db) -> MatchService:
    return MatchService(
        ApplicationRepository(db), StudentRepository(db), InternshipRepository(db), MatchRepository(db)
    )


@api_router.get("/applications")
def api_list_applications(user: AdminDep, db: SessionDep, q: str = "", show: str = "unmatched"):
    service = _match_service(db)
    rows = service.list_applications(q, unmatched_only=(show != "all"))
    placements = service.placements_for([a.id for a, _ in rows])
    return [
        {
            "application": a,
            "student": s,
            "placement": None if a.id not in placements else {
                "internship": placements[a.id][0],
                "company_name": placements[a.id][1].company_name,
            },
        }
        for a, s in rows
    ]


@api_router.get("/applications/{application_id}")
def api_get_application_for_match(application_id: int, user: AdminDep, db: SessionDep):
    service = _match_service(db)
    try:
        application, student = service.get_application(application_id)
    except MatchError as e:
        raise api_error(e)
    eligible = service.eligible_internships(student) if application.status == "submitted" else []
    return {
        "application": application,
        "student": student,
        "eligible_internships": [{**i.model_dump(), "company_name": c.company_name} for i, c in eligible],
    }


@api_router.patch("/applications/{application_id}")
def api_reject_application(application_id: int, body: ApplicationStatusUpdate, user: AdminDep, db: SessionDep):
    try:
        student = _match_service(db).reject_application(application_id)
    except MatchError as e:
        raise api_error(e)
    return {"id": application_id, "status": "rejected", "student": student}


@api_router.post("/matches", status_code=status.HTTP_201_CREATED)
def api_create_match(body: MatchCreate, user: AdminDep, db: SessionDep):
    try:
        match, internship = _match_service(db).match_application(body.application_id, body.internship_id)
    except MatchError as e:
        raise api_error(e)
    return {"match": match, "internship": internship}


@api_router.post("/companies", status_code=status.HTTP_201_CREATED)
def api_create_company(body: CompanyAccountForm, user: AdminDep, db: SessionDep):
    try:
        return CompanyService(UserRepository(db), CompanyRepository(db)).create_company_account(body)
    except CompanyError as e:
        raise api_error(e)
