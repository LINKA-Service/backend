from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError

from app.core.deps import get_current_lawyer, get_current_user, get_lawyer_service
from app.core.exceptions import ConflictException, NotFoundException
from app.models.lawyer import Lawyer
from app.models.user import User
from app.schemas.lawyer import (
    LawyerIdUpdate,
    LawyerResponse,
    LawyerReviewCreate,
    LawyerReviewResponse,
    ProfileUpdate,
)
from app.services.lawyer_service import LawyerService

router = APIRouter()


@router.get("/me", response_model=LawyerResponse)
async def get_me(current_lawyer: Annotated[Lawyer, Depends(get_current_lawyer)]):
    return current_lawyer


@router.put("/me", response_model=LawyerResponse)
async def update_me(
    profile_update: ProfileUpdate,
    current_lawyer: Annotated[Lawyer, Depends(get_current_lawyer)],
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    return lawyer_service.update_profile(current_lawyer.id, profile_update)


@router.get("/{lawyer_id}", response_model=LawyerResponse)
async def get_lawyer_by_lawyer_id(
    lawyer_id: str,
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    lawyer = lawyer_service.get_lawyer_by_lawyer_id(lawyer_id)
    if not lawyer:
        raise NotFoundException("Lawyer not found")
    return lawyer


@router.post("/change-lawyer-id", response_model=LawyerResponse)
async def change_lawyername(
    lawyer_id_update: LawyerIdUpdate,
    current_lawyer: Annotated[Lawyer, Depends(get_current_lawyer)],
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    try:
        return lawyer_service.update_lawyer_id(current_lawyer.id, lawyer_id_update)
    except IntegrityError:
        raise ConflictException("Lawyername already registered")


@router.get("/{lawyer_id}/reviews", response_model=List[LawyerReviewResponse])
async def get_lawyer_reviews(
    lawyer_id: int,
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    return lawyer_service.get_lawyer_reviews(lawyer_id)


@router.post("/{lawyer_id}/reviews", response_model=LawyerReviewResponse)
async def create_review(
    review: LawyerReviewCreate,
    lawyer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    return lawyer_service.create_review(review, lawyer_id, current_user.id)
