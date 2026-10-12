from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Match(SQLModel, table=True):
    """MATCH from the ERD. Created when the Admin matches an application to an internship."""

    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", unique=True)
    internship_id: int = Field(foreign_key="internship.id")
    matched_date: datetime = Field(default_factory=_utcnow)

    # ── MATCH SNIPPET (you complete) ──────────────────────────────────────
    # Add the remaining MATCH columns from the erDiagram in docs/report.md,
    # with the keys / constraints the ERD and the "final match" rule need.
    # (_utcnow above is available if you want it.)
    # TODO
    # ──────────────────────────────────────────────────────────────────────
