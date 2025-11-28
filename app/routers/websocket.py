from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session
import json

from ..database import get_db
from ..models.user import User
from ..models.channel import Channel
from ..models.message import Message
from ..services.websocket import manager
from ..services.auth import decode_access_token

router = APIRouter(tags=["websocket"])


async def get_user_from_token(token: str, db: Session) -> User:
    """Validate token and get user"""
    payload = decode_access_token(token)
    if not payload:
        return None

    username = payload.get("sub")
    if not username:
        return None

    user = db.query(User).filter(User.username == username).first()
    return user


@router.websocket("/ws/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    # Authenticate user
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Check if channel exists
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Check if user is a member of the server
    if user not in channel.server.members:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Connect to WebSocket
    await manager.connect(websocket, channel_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                content = message_data.get("content", "")

                if not content.strip():
                    continue

                # Save message to database
                new_message = Message(
                    content=content,
                    channel_id=channel_id,
                    author_id=user.id
                )
                db.add(new_message)
                db.commit()
                db.refresh(new_message)

                # Broadcast message to all connected clients in the channel
                broadcast_data = {
                    "id": new_message.id,
                    "content": new_message.content,
                    "channel_id": new_message.channel_id,
                    "author_id": new_message.author_id,
                    "author_username": user.username,
                    "created_at": new_message.created_at.isoformat(),
                    "updated_at": new_message.updated_at.isoformat()
                }

                await manager.broadcast(broadcast_data, channel_id)

            except json.JSONDecodeError:
                # If message is not JSON, treat as plain text
                new_message = Message(
                    content=data,
                    channel_id=channel_id,
                    author_id=user.id
                )
                db.add(new_message)
                db.commit()
                db.refresh(new_message)

                broadcast_data = {
                    "id": new_message.id,
                    "content": new_message.content,
                    "channel_id": new_message.channel_id,
                    "author_id": new_message.author_id,
                    "author_username": user.username,
                    "created_at": new_message.created_at.isoformat(),
                    "updated_at": new_message.updated_at.isoformat()
                }

                await manager.broadcast(broadcast_data, channel_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, channel_id)
