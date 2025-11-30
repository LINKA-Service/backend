from typing import Annotated, List

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user, get_group_service, get_message_service
from app.core.exceptions import ForbiddenException
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.services.group_service import GroupService
from app.services.message_service import MessageService

router = APIRouter()


@router.post("/", response_model=MessageResponse)
async def create_new_message(
    message: MessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    message_service: Annotated[MessageService, Depends(get_message_service)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    if not group_service.is_group_member(message.group_id, current_user.id):
        raise ForbiddenException("Not a member of this group")

    return message_service.create_message(message, current_user.id)


@router.get("/group/{group_id}", response_model=List[MessageResponse])
async def get_messages(
    group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[User, Depends(get_current_user)],
    message_service: Annotated[MessageService, Depends(get_message_service)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    if not group_service.is_group_member(group_id, current_user.id):
        raise ForbiddenException("Not a member of this group")

    return message_service.get_group_messages(group_id, skip, limit)


@router.delete("/{message_id}")
async def delete_message_by_id(
    message_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    message_service: Annotated[MessageService, Depends(get_message_service)],
):
    message_service.delete_message(message_id, current_user.id)
    return {"message": "Message deleted successfully"}
