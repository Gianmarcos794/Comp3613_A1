from pydantic import EmailStr
from sqlmodel import SQLModel


class CompanyAccountForm(SQLModel):
    """Fields of the Admin's 'add company' modal: USER login + COMPANY profile (ERD)."""
    username: str
    email: EmailStr
    password: str
    company_name: str
    contact_email: EmailStr
    industry: str
