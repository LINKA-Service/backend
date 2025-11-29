from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, get_user_service
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return user_service.update_user(current_user.id, user_update)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    user = user_service.get_user(user_id)
    if not user:
        raise NotFoundException("User not found")
    return user
