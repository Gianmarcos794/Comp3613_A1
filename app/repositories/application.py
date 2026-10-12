from sqlmodel import Session, select, or_
from app.models.application import Application
from app.models.student import Student
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_student(self, student_pk: int) -> Optional[Application]:
        return self.db.exec(select(Application).where(Application.student_id == student_pk)).one_or_none()

    def get_by_id(self, application_id: int) -> Optional[Application]:
        return self.db.get(Application, application_id)

    def search_with_students(self, query: str = "", status: Optional[str] = None) -> list[tuple[Application, Student]]:
        stmt = select(Application, Student).join(Student, Student.id == Application.student_id)
        if status:
            stmt = stmt.where(Application.status == status)
        if query:
            like = f"%{query}%"
            stmt = stmt.where(or_(
                Student.full_name.ilike(like),
                Student.student_id.ilike(like),
                Student.program.ilike(like),
            ))
        return self.db.exec(stmt.order_by(Application.submitted_date)).all()

    def save(self, application: Application) -> Application:
        try:
            self.db.add(application)
            self.db.commit()
            self.db.refresh(application)
            return application
        except Exception as e:
            logger.error(f"An error occurred while saving application: {e}")
            self.db.rollback()
            raise
