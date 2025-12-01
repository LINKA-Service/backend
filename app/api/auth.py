from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.deps import get_auth_service, get_current_user, get_user_service
from app.core.exceptions import ConflictException, UnauthorizedException
from app.db.redis import add_to_blacklist
from app.models import User
from app.schemas.user import (
    PasswordChange,
    StatusResponse,
    Token,
    UserCreate,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return auth_service.create_user(user=user)
    except IntegrityError:
        raise ConflictException("Username already registered")


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedException("Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "type": "normal"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", response_model=StatusResponse)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        exp = payload.get("exp")
        now = datetime.now(timezone.utc).timestamp()
        expires_in = (
            max(int(exp - now), 60)
            if exp
            else settings.access_token_expire_minutes * 60
        )

        await add_to_blacklist(token, expires_in)

    except Exception:
        pass

    return {"message": "Successfully logged out"}


@router.post("/change-password", response_model=StatusResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    auth_service.change_password(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )
    return {"message": "Password changed successfully"}
