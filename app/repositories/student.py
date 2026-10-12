from sqlmodel import Session, select
from app.models.student import Student
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class StudentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, student_pk: int) -> Optional[Student]:
        return self.db.get(Student, student_pk)

    def get_by_user_id(self, user_id: int) -> Optional[Student]:
        return self.db.exec(select(Student).where(Student.user_id == user_id)).one_or_none()

    def get_by_student_number(self, student_number: str) -> Optional[Student]:
        return self.db.exec(select(Student).where(Student.student_id == student_number)).one_or_none()

    def save(self, student: Student) -> Student:
        try:
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)
            return student
        except Exception as e:
            logger.error(f"An error occurred while saving student: {e}")
            self.db.rollback()
            raise
