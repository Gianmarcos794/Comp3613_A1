from sqlmodel import Session, select
from app.models.company import Company
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[Company]:
        return self.db.exec(select(Company).where(Company.user_id == user_id)).one_or_none()

    def get_all(self) -> list[Company]:
        return self.db.exec(select(Company).order_by(Company.company_name)).all()

    def save(self, company: Company) -> Company:
        try:
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            return company
        except Exception as e:
            logger.error(f"An error occurred while saving company: {e}")
            self.db.rollback()
            raise
