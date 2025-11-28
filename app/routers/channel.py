from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.server import Server
from ..models.channel import Channel
from ..models.message import Message
from ..schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse
from ..schemas.message import MessageResponse, MessageWithAuthor
from ..dependencies.auth import get_current_active_user

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
def create_channel(
    channel_data: ChannelCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new channel (sub chat room) in a server"""
    server = db.query(Server).filter(Server.id == channel_data.server_id).first()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    # Only server owner can create channels
    if server.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the server owner can create channels"
        )

    new_channel = Channel(
        name=channel_data.name,
        description=channel_data.description,
        server_id=channel_data.server_id
    )

    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)

    return new_channel


@router.get("/{channel_id}", response_model=ChannelResponse)
def get_channel(
    channel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific channel"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )

    # Check if user is a member of the server
    if current_user not in channel.server.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this server"
        )

    return channel


@router.put("/{channel_id}", response_model=ChannelResponse)
def update_channel(
    channel_id: int,
    channel_update: ChannelUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a channel (only server owner can update)"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )

    if channel.server.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the server owner can update channels"
        )

    if channel_update.name is not None:
        channel.name = channel_update.name

    if channel_update.description is not None:
        channel.description = channel_update.description

    db.commit()
    db.refresh(channel)

    return channel


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_channel(
    channel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a channel (only server owner can delete)"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )

    if channel.server.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the server owner can delete channels"
        )

    db.delete(channel)
    db.commit()

    return None


@router.get("/{channel_id}/messages", response_model=List[MessageWithAuthor])
def get_channel_messages(
    channel_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages from a channel"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )

    # Check if user is a member of the server
    if current_user not in channel.server.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this server"
        )

    messages = db.query(Message).filter(
        Message.channel_id == channel_id
    ).order_by(Message.created_at.desc()).offset(offset).limit(limit).all()

    # Format messages with author username
    result = []
    for message in messages:
        message_dict = {
            "id": message.id,
            "content": message.content,
            "channel_id": message.channel_id,
            "author_id": message.author_id,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "author_username": message.author.username
        }
        result.append(message_dict)

    return result
