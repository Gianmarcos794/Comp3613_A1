from sqlmodel import SQLModel


class ApplicationForm(SQLModel):
    """Fields on the Application form / Edit application wireframe (email comes from USER)."""
    full_name: str
    student_id: str
    program: str
    year_of_study: int
    gpa: float
    projects: str = ""
    preferences: str = ""
