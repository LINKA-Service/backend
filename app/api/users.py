from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError

from app.core.deps import get_current_user, get_user_service
from app.core.exceptions import ConflictException, NotFoundException
from app.models.user import User
from app.schemas.user import ProfileUpdate, UsernameUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    profile_update: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return user_service.update_profile(current_user.id, profile_update)


@router.get("/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = user_service.get_user_by_username(username)
    if not user:
        raise NotFoundException("User not found")
    return user


@router.post("/change-username", response_model=UserResponse)
async def change_username(
    username_update: UsernameUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return user_service.update_username(current_user.id, username_update)
    except IntegrityError:
        raise ConflictException("Username already registered")
