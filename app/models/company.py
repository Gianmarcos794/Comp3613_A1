from typing import Optional

from sqlmodel import Field, SQLModel


class Company(SQLModel, table=True):
    """COMPANY profile from the ERD. Created by the Admin (Create Company Account)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    company_name: str
    contact_email: str
    industry: str

    # ── COMPANY SNIPPET (you complete) ────────────────────────────────────
    # Add the remaining COMPANY columns from the erDiagram in docs/report.md,
    # with the keys / constraints the ERD shows.
    # TODO
    # ──────────────────────────────────────────────────────────────────────
