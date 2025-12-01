from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError

from app.core.deps import get_current_lawyer, get_lawyer_service
from app.core.exceptions import ConflictException, NotFoundException
from app.models.lawyer import Lawyer
from app.schemas.lawyer import (
    LawyerResponse,
    LawyerReviewCreate,
    LawyerReviewResponse,
    LawyernameUpdate,
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


@router.get("/{lawyername}", response_model=LawyerResponse)
async def get_lawyer_by_lawyername(
    lawyername: str,
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    lawyer = lawyer_service.get_lawyer_by_lawyername(lawyername)
    if not lawyer:
        raise NotFoundException("Lawyer not found")
    return lawyer


@router.post("/change-lawyername", response_model=LawyerResponse)
async def change_lawyername(
    lawyername_update: LawyernameUpdate,
    current_lawyer: Annotated[Lawyer, Depends(get_current_lawyer)],
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    try:
        return lawyer_service.update_lawyername(
            current_lawyer.id, lawyername_update
        )
    except IntegrityError:
        raise ConflictException("Lawyername already registered")


@router.get("/{lawyername}/reviews", response_model=List[LawyerReviewResponse])
async def get_lawyer_reviews(
    lawyername: str,
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    return lawyer_service.get_lawyer_reviews(lawyername)


@router.post("/reviews", response_model=LawyerReviewResponse)
async def create_review(
    review: LawyerReviewCreate,
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    return lawyer_service.create_review(review)
