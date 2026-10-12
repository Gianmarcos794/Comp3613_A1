from datetime import date
from sqlmodel import Session, select, func
from app.models.company import Company
from app.models.internship import Internship
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class InternshipRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, internship_id: int) -> Optional[Internship]:
        return self.db.get(Internship, internship_id)

    def get_by_company(self, company_id: int) -> list[Internship]:
        return self.db.exec(
            select(Internship)
            .where(Internship.company_id == company_id)
            .order_by(Internship.status.desc(), Internship.deadline)  # open before closed
        ).all()

    def get_all_with_company(self) -> list[tuple[Internship, Company]]:
        return self.db.exec(
            select(Internship, Company)
            .join(Company, Company.id == Internship.company_id)
            .order_by(Internship.status.desc(), Internship.deadline)
        ).all()

    def find_matching(
        self, program: str, gpa: float, year: int, status: str, deadline_from: date
    ) -> list[tuple[Internship, Company]]:
        return self.db.exec(
            select(Internship, Company)
            .join(Company, Company.id == Internship.company_id)
            .where(
                Internship.status == status,
                func.lower(func.trim(Internship.required_program)) == program.strip().lower(),
                Internship.minimum_gpa <= gpa,
                Internship.minimum_year <= year,
                Internship.deadline >= deadline_from,
            )
            .order_by(Internship.deadline)
        ).all()

    def save(self, internship: Internship) -> Internship:
        try:
            self.db.add(internship)
            self.db.commit()
            self.db.refresh(internship)
            return internship
        except Exception as e:
            logger.error(f"An error occurred while saving internship: {e}")
            self.db.rollback()
            raise
