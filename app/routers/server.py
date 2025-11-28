from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.server import Server
from ..schemas.server import ServerCreate, ServerUpdate, ServerResponse, ServerWithChannels
from ..dependencies.auth import get_current_active_user

router = APIRouter(prefix="/servers", tags=["servers"])


@router.post("/", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
def create_server(
    server_data: ServerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new server (main chat room)"""
    new_server = Server(
        name=server_data.name,
        description=server_data.description,
        icon_url=server_data.icon_url,
        owner_id=current_user.id
    )

    # Add creator as a member
    new_server.members.append(current_user)

    db.add(new_server)
    db.commit()
    db.refresh(new_server)

    return new_server


@router.get("/", response_model=List[ServerResponse])
def get_my_servers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all servers that the current user is a member of"""
    return current_user.servers


@router.get("/{server_id}", response_model=ServerWithChannels)
def get_server(
    server_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific server with its channels"""
    server = db.query(Server).filter(Server.id == server_id).first()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    # Check if user is a member
    if current_user not in server.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this server"
        )

    return server


@router.put("/{server_id}", response_model=ServerResponse)
def update_server(
    server_id: int,
    server_update: ServerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a server (only owner can update)"""
    server = db.query(Server).filter(Server.id == server_id).first()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    if server.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the server owner can update the server"
        )

    if server_update.name is not None:
        server.name = server_update.name

    if server_update.description is not None:
        server.description = server_update.description

    if server_update.icon_url is not None:
        server.icon_url = server_update.icon_url

    db.commit()
    db.refresh(server)

    return server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_server(
    server_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a server (only owner can delete)"""
    server = db.query(Server).filter(Server.id == server_id).first()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    if server.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the server owner can delete the server"
        )

    db.delete(server)
    db.commit()

    return None


@router.post("/{server_id}/join", response_model=ServerResponse)
def join_server(
    server_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join a server"""
    server = db.query(Server).filter(Server.id == server_id).first()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    if current_user in server.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this server"
        )

    server.members.append(current_user)
    db.commit()
    db.refresh(server)

    return server


@router.post("/{server_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_server(
    server_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Leave a server"""
    server = db.query(Server).filter(Server.id == server_id).first()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    if server.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server owner cannot leave. Transfer ownership or delete the server."
        )

    if current_user not in server.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this server"
        )

    server.members.remove(current_user)
    db.commit()

    return None
