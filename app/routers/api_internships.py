"""JSON API: Publish/Manage Internships (Company)."""

from fastapi import status

from app.dependencies import CompanyDep, SessionDep
from app.repositories.company import CompanyRepository
from app.repositories.internship import InternshipRepository
from app.repositories.match import MatchRepository
from app.schemas.internship import InternshipForm, InternshipStatusUpdate
from app.services.internship_service import InternshipError, InternshipService
from . import api_router
from .api_auth import api_error


def _service(db) -> InternshipService:
    return InternshipService(CompanyRepository(db), InternshipRepository(db), MatchRepository(db))


@api_router.get("/internships")
def api_list_internships(user: CompanyDep, db: SessionDep):
    try:
        _, internships, counts = _service(db).list_for_company(user)
    except InternshipError as e:
        raise api_error(e)
    return [{**i.model_dump(), "matched_count": counts.get(i.id, 0)} for i in internships]


@api_router.post("/internships", status_code=status.HTTP_201_CREATED)
def api_create_internship(body: InternshipForm, user: CompanyDep, db: SessionDep):
    try:
        return _service(db).create_internship(user, body)
    except InternshipError as e:
        raise api_error(e)


@api_router.get("/internships/{internship_id}")
def api_get_internship(internship_id: int, user: CompanyDep, db: SessionDep):
    try:
        return _service(db).get_owned(user, internship_id)
    except InternshipError as e:
        raise api_error(e)


@api_router.put("/internships/{internship_id}")
def api_update_internship(internship_id: int, body: InternshipForm, user: CompanyDep, db: SessionDep):
    try:
        return _service(db).update_internship(user, internship_id, body)
    except InternshipError as e:
        raise api_error(e)


@api_router.patch("/internships/{internship_id}")
def api_close_internship(internship_id: int, body: InternshipStatusUpdate, user: CompanyDep, db: SessionDep):
    try:
        return _service(db).close_internship(user, internship_id)
    except InternshipError as e:
        raise api_error(e)


@api_router.get("/internships/{internship_id}/matches")
def api_internship_matches(internship_id: int, user: CompanyDep, db: SessionDep):
    try:
        _, matches = _service(db).matched_students(user, internship_id)
    except InternshipError as e:
        raise api_error(e)
    return [
        {"match_id": m.id, "matched_date": m.matched_date, "email": u.email, "student": s}
        for m, s, u in matches
    ]
