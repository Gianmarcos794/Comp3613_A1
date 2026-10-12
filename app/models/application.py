from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Application(SQLModel, table=True):
    """APPLICATION from the ERD. One per student (student_id is unique)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", unique=True, index=True)
    preferences: str = ""
    projects: str = ""
    submitted_date: datetime = Field(default_factory=_utcnow)
    status: str = Field(default="submitted", index=True)  # submitted | matched | rejected
