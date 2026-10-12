"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.user import User
from app.models.student import Student
from app.models.application import Application
from app.models.company import Company
from app.models.internship import Internship
from app.models.match import Match

__all__ = ["User", "Student", "Application", "Company", "Internship", "Match"]
