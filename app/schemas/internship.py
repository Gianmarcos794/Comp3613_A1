from datetime import date
from typing import Literal

from sqlmodel import Field, SQLModel


class InternshipForm(SQLModel):
    """Fields on the Internship Form wireframe (new / edit)."""
    title: str
    description: str
    location: str
    required_program: str
    minimum_gpa: float = Field(ge=0)
    minimum_year: int = Field(ge=1)
    number_of_positions: int = Field(ge=1)
    deadline: date


class InternshipStatusUpdate(SQLModel):
    """PATCH body for the API: the only status change a company can make is closing."""
    status: Literal["closed"]
