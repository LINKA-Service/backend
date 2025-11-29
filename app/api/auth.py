from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.deps import get_auth_service, get_user_service
from app.core.exceptions import ConflictException, UnauthorizedException
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    db_user = user_service.get_user_by_username(username=user.username)
    if db_user:
        raise ConflictException("Username already registered")

    db_user = user_service.get_user_by_email(email=user.email)
    if db_user:
        raise ConflictException("Email already registered")

    return auth_service.create_user(user=user)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedException("Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
