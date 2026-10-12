from datetime import date

from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.application import ApplicationRepository
from app.repositories.company import CompanyRepository
from app.repositories.internship import InternshipRepository
from app.repositories.match import MatchRepository
from app.repositories.student import StudentRepository
from app.services.application_service import ApplicationService
from app.services.internship_service import InternshipService, InternshipError
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    if user.role == "company":
        service = InternshipService(CompanyRepository(db), InternshipRepository(db), MatchRepository(db))
        try:
            company, internships, match_counts = service.list_for_company(user)
        except InternshipError:
            company, internships, match_counts = None, [], {}
        return templates.TemplateResponse(
            request=request,
            name="company_home.html",
            context={
                "user": user,
                "company": company,
                "internships": internships,
                "match_counts": match_counts,
                "today": date.today(),
            }
        )

    student = application = placement = None
    if user.role == "student":
        service = ApplicationService(StudentRepository(db), ApplicationRepository(db), MatchRepository(db))
        student, application = service.get_for_user(user)
        placement = service.get_placement(application)

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "student": student,
            "application": application,
            "placement": placement,
        }
    )
