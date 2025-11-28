from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserResponse, UserUpdate
from ..dependencies.auth import get_current_active_user
from ..services.auth import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    if user_update.display_name is not None:
        current_user.display_name = user_update.display_name

    if user_update.bio is not None:
        current_user.bio = user_update.bio

    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url

    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get another user's profile"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
