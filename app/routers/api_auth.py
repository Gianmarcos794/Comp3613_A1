"""JSON API: register and log in (returns a Bearer token for Postman / API clients)."""

from fastapi import HTTPException, status

from app.dependencies import SessionDep
from app.repositories.user import UserRepository
from app.schemas.auth import SigninRequest, SignupRequest
from app.services.auth_service import AuthService, RegistrationError
from . import api_router


def api_error(e: Exception) -> HTTPException:
    """Turn a service refusal into an HTTP error: 404 for missing records, 400 for broken rules."""
    message = str(e)
    code = status.HTTP_404_NOT_FOUND if "not found" in message.lower() else status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=message)


@api_router.post("/register", status_code=status.HTTP_201_CREATED)
def api_register(body: SignupRequest, db: SessionDep):
    try:
        user = AuthService(UserRepository(db)).register_user(body.username, body.email, body.password)
    except RegistrationError as e:
        raise api_error(e)
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role}


@api_router.post("/login")
def api_login(body: SigninRequest, db: SessionDep):
    user_repo = UserRepository(db)
    token = AuthService(user_repo).authenticate_user(body.username, body.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    user = user_repo.get_by_username(body.username)
    return {"access_token": token, "token_type": "bearer", "role": user.role}
