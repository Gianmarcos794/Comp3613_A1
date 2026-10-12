from typing import Optional

from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    """STUDENT profile from the ERD. Created on the student's first application submit."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    full_name: str
    student_id: str = Field(unique=True)
    program: str
    year_of_study: int
    gpa: float

    # ── STUDENT SNIPPET (you complete) ────────────────────────────────────
    # Add the remaining STUDENT columns from the erDiagram in docs/report.md,
    # with the keys / constraints the ERD shows.
    # TODO
    # ──────────────────────────────────────────────────────────────────────
