from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel
from enum import Enum

class InternshipStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class Internship(SQLModel, table=True):
    """INTERNSHIP from the ERD. Posted by a company; status is open | closed."""

    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id")
    title: str
    description: str
    location: str
    required_program: str
    minimum_gpa: float
    minimum_year: int
    number_of_positions: int
    deadline: date
    status: InternshipStatus = Field(default=InternshipStatus.OPEN)

    # ── INTERNSHIP SNIPPET (you complete) ─────────────────────────────────
    # Add the remaining INTERNSHIP columns from the erDiagram in docs/report.md,
    # with the keys / constraints / defaults the ERD and your rules need.
    # TODO
    # ──────────────────────────────────────────────────────────────────────
