from app.repositories.user import UserRepository
from app.utilities.security import encrypt_password, verify_password, create_access_token
from app.schemas.user import StudentUserCreate
from typing import Optional


class RegistrationError(Exception):
    """A sign-up the rules refuse; the message is safe to show the student."""


def is_edu_email(email: str) -> bool:
    domain = email.rsplit("@", 1)[-1].strip().lower()
    return "@" in email and domain.endswith(".edu")


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(plaintext_password=password, encrypted_password=user.password):
            return None
        access_token = create_access_token(data={"sub": f"{user.id}", "role": user.role})
        return access_token

    def register_user(self, username: str, email: str, password: str):
        if not is_edu_email(email):
            raise RegistrationError("Please sign up with your university email (an address ending in .edu).")
        if self.user_repo.get_by_username(username) or self.user_repo.get_by_email(email):
            raise RegistrationError("Username or email already exists")
        new_user = StudentUserCreate(
            username=username, 
            email=email, 
            password=encrypt_password(password)
        )
        return self.user_repo.create(new_user)
