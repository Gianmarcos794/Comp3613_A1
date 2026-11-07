from typing import Literal

from sqlmodel import Field, SQLModel


class ApplicationForm(SQLModel):
    """Fields on the Application form / Edit application wireframe (email comes from USER)."""
    full_name: str
    student_id: str
    program: str
    year_of_study: int = Field(ge=1)
    gpa: float = Field(ge=0)
    projects: str = ""
    preferences: str = ""


class ApplicationStatusUpdate(SQLModel):
    """PATCH body for the API: the Admin rejects an application (Reject Application «extend»)."""
    status: Literal["rejected"]


class MatchCreate(SQLModel):
    """POST /api/matches body: Match Application to Internship."""
    application_id: int
    internship_id: int
