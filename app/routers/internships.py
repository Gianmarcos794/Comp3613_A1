from datetime import date

from fastapi import Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import SessionDep, CompanyDep
from app.repositories.company import CompanyRepository
from app.repositories.internship import InternshipRepository
from app.repositories.match import MatchRepository
from app.schemas.internship import InternshipForm
from app.services.internship_service import InternshipService, InternshipError
from app.utilities.flash import flash
from . import router, templates


def _service(db) -> InternshipService:
    return InternshipService(CompanyRepository(db), InternshipRepository(db), MatchRepository(db))


def _to_dashboard(request: Request) -> RedirectResponse:
    return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)


# View route: Internship Form (new)
@router.get("/app/internships/new", response_class=HTMLResponse)
async def new_internship_view(request: Request, user: CompanyDep):
    return templates.TemplateResponse(
        request=request,
        name="internship_form.html",
        context={"user": user, "internship": None},
    )


# Action route: Save a new internship
@router.post("/app/internships", response_class=HTMLResponse)
def create_internship_action(
    request: Request,
    user: CompanyDep,
    db: SessionDep,
    title: str = Form(),
    description: str = Form(),
    location: str = Form(),
    required_program: str = Form(),
    minimum_gpa: float = Form(ge=0),
    minimum_year: int = Form(ge=1),
    number_of_positions: int = Form(ge=1),
    deadline: date = Form(),
):
    service = InternshipService(CompanyRepository(db), InternshipRepository(db), MatchRepository(db))
    form = InternshipForm(
        title=title, description=description, location=location,
        required_program=required_program, minimum_gpa=minimum_gpa,
        minimum_year=minimum_year, number_of_positions=number_of_positions, deadline=deadline,
    )
    try:
        internship = service.create_internship(user, form)
    except InternshipError as e:
        flash(request, str(e), "danger")
        return RedirectResponse(url=request.url_for("new_internship_view"), status_code=status.HTTP_303_SEE_OTHER)
    
    flash(request, f"Created {internship.title}.")
    return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)
    # ── ROUTE SNIPPET (you complete) ──────────────────────────────────────
    # Publish an internship: save the form, then follow the wireframe
    # (Save -> Company dashboard). If it is refused, show the reason and
    # return to the Internship Form. Keep the route thin.
    # TODO
    # ──────────────────────────────────────────────────────────────────────
    ...


# View route: Internship Form (edit)
@router.get("/app/internships/{internship_id}/edit", response_class=HTMLResponse)
async def edit_internship_view(request: Request, internship_id: int, user: CompanyDep, db: SessionDep):
    try:
        internship = _service(db).get_owned(user, internship_id)
        if internship.status == "closed":
            raise InternshipError("This internship is closed and can no longer be edited.")
    except InternshipError as e:
        flash(request, str(e), "danger")
        return _to_dashboard(request)
    return templates.TemplateResponse(
        request=request,
        name="internship_form.html",
        context={"user": user, "internship": internship},
    )


# Action route: Save edits
@router.post("/app/internships/{internship_id}", response_class=HTMLResponse)
def update_internship_action(
    request: Request,
    internship_id: int,
    user: CompanyDep,
    db: SessionDep,
    title: str = Form(),
    description: str = Form(),
    location: str = Form(),
    required_program: str = Form(),
    minimum_gpa: float = Form(ge=0),
    minimum_year: int = Form(ge=1),
    number_of_positions: int = Form(ge=1),
    deadline: date = Form(),
):
    form = InternshipForm(
        title=title, description=description, location=location,
        required_program=required_program, minimum_gpa=minimum_gpa,
        minimum_year=minimum_year, number_of_positions=number_of_positions, deadline=deadline,
    )
    try:
        internship = _service(db).update_internship(user, internship_id, form)
    except InternshipError as e:
        flash(request, str(e), "danger")
        return RedirectResponse(
            url=request.url_for("edit_internship_view", internship_id=internship_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    flash(request, f"Saved {internship.title}.")
    return _to_dashboard(request)


# Action route: Close
@router.post("/app/internships/{internship_id}/close", response_class=HTMLResponse)
def close_internship_action(request: Request, internship_id: int, user: CompanyDep, db: SessionDep):
    try:
        internship = _service(db).close_internship(user, internship_id)
        flash(request, f"Closed {internship.title}. It will get no new matches.")
    except InternshipError as e:
        flash(request, str(e), "danger")
    return _to_dashboard(request)


# View route: View matches
@router.get("/app/internships/{internship_id}/matches", response_class=HTMLResponse)
async def internship_matches_view(request: Request, internship_id: int, user: CompanyDep, db: SessionDep):
    try:
        internship, matches = _service(db).matched_students(user, internship_id)
    except InternshipError as e:
        flash(request, str(e), "danger")
        return _to_dashboard(request)
    return templates.TemplateResponse(
        request=request,
        name="internship_matches.html",
        context={"user": user, "internship": internship, "matches": matches},
    )
