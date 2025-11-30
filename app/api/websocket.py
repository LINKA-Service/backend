import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
from app.schemas.message import MessageCreate
from app.services.group_service import GroupService
from app.services.message_service import MessageService
from app.services.websocket_service import manager

router = APIRouter()


async def get_user_from_token(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.id == int(user_id)).first()
    return user


@router.websocket("/{group_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    group_id: int,
    token: Annotated[str, Query(...)],
    db: Annotated[Session, Depends(get_db)],
):
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008)
        return

    group_service = GroupService(db)
    if not group_service.is_group_member(group_id, user.id):
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, group_id)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            message_create = MessageCreate(
                content=message_data.get("content"), group_id=group_id
            )

            message_service = MessageService(db)
            db_message = message_service.create_message(message_create, user.id)

            response = {
                "id": db_message.id,
                "content": db_message.content,
                "author_id": user.id,
                "author_username": user.username,
                "author_display_name": user.display_name or user.username,
                "created_at": db_message.created_at.isoformat(),
            }

            await manager.broadcast(json.dumps(response), group_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, group_id)
