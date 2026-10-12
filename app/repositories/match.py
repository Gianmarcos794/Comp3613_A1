from typing import Optional
from sqlmodel import Session, select, func
from app.models.application import Application
from app.models.company import Company
from app.models.internship import Internship
from app.models.match import Match
from app.models.student import Student
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_for_internship(self, internship_id: int) -> int:
        return self.db.exec(
            select(func.count()).select_from(Match).where(Match.internship_id == internship_id)
        ).one()

    def counts_for_internships(self, internship_ids: list[int]) -> dict[int, int]:
        if not internship_ids:
            return {}
        rows = self.db.exec(
            select(Match.internship_id, func.count())
            .where(Match.internship_id.in_(internship_ids))
            .group_by(Match.internship_id)
        ).all()
        return {internship_id: count for internship_id, count in rows}

    def get_matched_students(self, internship_id: int) -> list[tuple[Match, Student, User]]:
        return self.db.exec(
            select(Match, Student, User)
            .join(Application, Application.id == Match.application_id)
            .join(Student, Student.id == Application.student_id)
            .join(User, User.id == Student.user_id)
            .where(Match.internship_id == internship_id)
            .order_by(Match.matched_date)
        ).all()

    def get_placements(self, application_ids: list[int]) -> dict[int, tuple[Internship, Company]]:
        if not application_ids:
            return {}
        rows = self.db.exec(
            select(Match.application_id, Internship, Company)
            .join(Internship, Internship.id == Match.internship_id)
            .join(Company, Company.id == Internship.company_id)
            .where(Match.application_id.in_(application_ids))
        ).all()
        return {application_id: (internship, company) for application_id, internship, company in rows}

    def get_placement(self, application_id: int) -> Optional[tuple[Match, Internship, Company]]:
        return self.db.exec(
            select(Match, Internship, Company)
            .join(Internship, Internship.id == Match.internship_id)
            .join(Company, Company.id == Internship.company_id)
            .where(Match.application_id == application_id)
        ).one_or_none()

    def create_match(self, match: Match, application: Application, internship: Internship) -> Match:
        """Save the match and the updated application / internship in one commit."""
        try:
            self.db.add(match)
            self.db.add(application)
            self.db.add(internship)
            self.db.commit()
            self.db.refresh(match)
            return match
        except Exception as e:
            logger.error(f"An error occurred while saving match: {e}")
            self.db.rollback()
            raise
