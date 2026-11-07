from datetime import date
from typing import Optional

from sqlmodel import AutoString, Field, SQLModel
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
    # Stored as plain text ("open" / "closed"), matching existing rows and the services.
    # Without sa_type, SQLAlchemy stores enum NAMES ("OPEN") and crashes reading "open".
    status: InternshipStatus = Field(default=InternshipStatus.OPEN, sa_type=AutoString)

    # ── INTERNSHIP SNIPPET (you complete) ─────────────────────────────────
    # Add the remaining INTERNSHIP columns from the erDiagram in docs/report.md,
    # with the keys / constraints / defaults the ERD and your rules need.
    # TODO
    # ──────────────────────────────────────────────────────────────────────
