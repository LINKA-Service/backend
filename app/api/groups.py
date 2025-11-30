from typing import Annotated, List

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user, get_group_service
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.user import User
from app.schemas.group import GroupCreate, GroupResponse, GroupUpdate
from app.schemas.message import MessageCreate, MessageResponse
from app.services.group_service import GroupService

router = APIRouter()


@router.get("/", response_model=List[GroupResponse])
async def list_my_groups(
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    return group_service.get_user_groups(current_user.id)


@router.post("/", response_model=GroupResponse)
async def create_new_group(
    group: GroupCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    return group_service.create_group(group, current_user.id)


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group_detail(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    group = group_service.get_group(group_id)
    if not group:
        raise NotFoundException("Group not found")
    return group


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group_detail(
    group_id: int,
    group_update: GroupUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    return group_service.update_group(group_id, group_update, current_user.id)


@router.delete("/{group_id}")
async def delete_group_by_id(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    group_service.delete_group(group_id, current_user.id)
    return {"message": "Group deleted successfully"}


@router.post("/{group_id}/join", response_model=GroupResponse)
async def join_group_by_id(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    return group_service.join_group(group_id, current_user.id)


@router.post("/{group_id}/leave")
async def leave_group_by_id(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    group_service.leave_group(group_id, current_user.id)
    return {"message": "Left group successfully"}


@router.post("/{group_id}/messages", response_model=MessageResponse)
async def create_new_message(
    group_id: int,
    message: MessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    if not group_service.is_group_member(group_id, current_user.id):
        raise ForbiddenException("Not a member of this group")

    return group_service.create_message(message, current_user.id)


@router.get("/{group_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    if not group_service.is_group_member(group_id, current_user.id):
        raise ForbiddenException("Not a member of this group")

    return group_service.get_group_messages(group_id, skip, limit)


@router.delete("/messages/{message_id}")
async def delete_message_by_id(
    message_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
):
    group_service.delete_message(message_id, current_user.id)
    return {"message": "Message deleted successfully"}
