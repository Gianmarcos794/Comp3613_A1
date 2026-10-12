from fastapi import Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import SessionDep, StudentDep
from app.repositories.application import ApplicationRepository
from app.repositories.student import StudentRepository
from app.schemas.application import ApplicationForm
from app.services.application_service import ApplicationService, ApplicationError
from app.utilities.flash import flash
from . import router, templates


# View route: Application form (first submit) / Edit application (resubmit)
@router.get("/app/application", response_class=HTMLResponse)
async def application_form_view(request: Request, user: StudentDep, db: SessionDep):
    service = ApplicationService(StudentRepository(db), ApplicationRepository(db))
    student, application = service.get_for_user(user)
    if application and application.status == "matched":
        flash(request, "Your application has been matched and can no longer be changed.", "warning")
        return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="application_form.html",
        context={"user": user, "student": student, "application": application},
    )


# Action route: Submit application / Resubmit
@router.post("/app/application", response_class=HTMLResponse)
def submit_application_action(
    request: Request,
    user: StudentDep,
    db: SessionDep,
    full_name: str = Form(),
    student_id: str = Form(),
    program: str = Form(),
    year_of_study: int = Form(ge=1),
    gpa: float = Form(ge=0),
    projects: str = Form(""),
    preferences: str = Form(""),
):
    form = ApplicationForm(
        full_name=full_name,
        student_id=student_id,
        program=program,
        year_of_study=year_of_study,
        gpa=gpa,
        projects=projects,
        preferences=preferences,
    )
    service = ApplicationService(StudentRepository(db), ApplicationRepository(db))
    try:
        service.submit_application(user, form)
    except ApplicationError as e:
        flash(request, str(e), "danger")
        return RedirectResponse(url=request.url_for("application_form_view"), status_code=status.HTTP_303_SEE_OTHER)

    flash(request, "Application submitted.", "success")
    return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)
