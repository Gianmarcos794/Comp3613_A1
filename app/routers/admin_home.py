from datetime import date

from fastapi import Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep
from app.repositories.application import ApplicationRepository
from app.repositories.company import CompanyRepository
from app.repositories.internship import InternshipRepository
from app.repositories.match import MatchRepository
from app.repositories.student import StudentRepository
from app.repositories.user import UserRepository
from app.schemas.company import CompanyAccountForm
from app.services.company_service import CompanyService, CompanyError
from app.services.match_service import MatchService, MatchError
from app.utilities.flash import flash
from . import router, templates


def _match_service(db) -> MatchService:
    return MatchService(
        ApplicationRepository(db), StudentRepository(db), InternshipRepository(db), MatchRepository(db)
    )


def _to_dashboard(request: Request) -> RedirectResponse:
    return RedirectResponse(url=request.url_for("admin_home_view"), status_code=status.HTTP_303_SEE_OTHER)


# View route: Admin dashboard (Students / Internship header buttons)
@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    view: str = "students",
    show: str = "unmatched",
    q: str = "",
):
    service = _match_service(db)
    context = {"user": user, "view": view, "show": show, "q": q, "today": date.today()}
    if view == "internships":
        context["internships"], context["match_counts"] = service.list_internships()
    else:
        context["view"] = "students"
        applications = service.list_applications(q, unmatched_only=(show != "all"))
        context["applications"] = applications
        context["placements"] = service.placements_for([a.id for a, _ in applications])
    return templates.TemplateResponse(request=request, name="admin.html", context=context)


# View route: Match Application
@router.get("/admin/applications/{application_id}", response_class=HTMLResponse)
async def match_application_view(request: Request, application_id: int, user: AdminDep, db: SessionDep):
    service = _match_service(db)
    try:
        application, student = service.get_application(application_id)
    except MatchError as e:
        flash(request, str(e), "danger")
        return _to_dashboard(request)
    eligible = service.eligible_internships(student) if application.status == "submitted" else []
    return templates.TemplateResponse(
        request=request,
        name="admin_application.html",
        context={"user": user, "application": application, "student": student, "eligible": eligible},
    )


# Action route: match
@router.post("/admin/applications/{application_id}/match", response_class=HTMLResponse)
def match_application_action(
    request: Request,
    application_id: int,
    user: AdminDep,
    db: SessionDep,
    internship_id: int = Form(),
):
    service = _match_service(db)
    try:
        service.match_application(application_id, internship_id)
        flash(request, "Application matched successfully.")
    except MatchError as e:
        flash(request, str(e), "danger")
        return RedirectResponse(
            url=request.url_for("match_application_view", application_id=application_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return _to_dashboard(request)
    # ── ROUTE SNIPPET (you complete) ──────────────────────────────────────
    # Match Application to Internship: match this application to the chosen
    # internship, then follow the wireframe (match -> Admin dashboard).
    # If the match is refused, show the reason and return to the
    # Match Application screen. Keep the route thin.
    # TODO
    # ──────────────────────────────────────────────────────────────────────
    ...


# Action route: reject (Reject Application «extend»)
@router.post("/admin/applications/{application_id}/reject", response_class=HTMLResponse)
def reject_application_action(request: Request, application_id: int, user: AdminDep, db: SessionDep):
    try:
        student = _match_service(db).reject_application(application_id)
        flash(request, f"Rejected {student.full_name}'s application. They can update it and resubmit.")
    except MatchError as e:
        flash(request, str(e), "danger")
        return RedirectResponse(
            url=request.url_for("match_application_view", application_id=application_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return _to_dashboard(request)


# Action route: Create Company Account ("add company" modal)
@router.post("/admin/companies", response_class=HTMLResponse)
def create_company_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
    company_name: str = Form(),
    contact_email: str = Form(),
    industry: str = Form(),
):
    try:
        form = CompanyAccountForm(
            username=username,
            email=email,
            password=password,
            company_name=company_name,
            contact_email=contact_email,
            industry=industry,
        )
        service = CompanyService(UserRepository(db), CompanyRepository(db))
        company = service.create_company_account(form)
        flash(request, f"Company account created for {company.company_name}.")
    except (CompanyError, ValueError) as e:
        message = str(e) if isinstance(e, CompanyError) else "Please enter valid email addresses."
        flash(request, message, "danger")
    return _to_dashboard(request)
