from datetime import date
from sqlmodel import SQLModel


class InternshipForm(SQLModel):
    """Fields on the Internship Form wireframe (new / edit)."""
    title: str
    description: str
    location: str
    required_program: str
    minimum_gpa: float
    minimum_year: int
    number_of_positions: int
    deadline: date
