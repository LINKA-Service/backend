from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.message import Message
from app.schemas.message import MessageCreate


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message: MessageCreate, author_id: int) -> Message:
        db_message = Message(
            content=message.content, group_id=message.group_id, author_id=author_id
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_group_messages(
        self, group_id: int, skip: int = 0, limit: int = 50
    ) -> List[Message]:
        return (
            self.db.query(Message)
            .filter(Message.group_id == group_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_message(self, message_id: int, user_id: int) -> None:
        db_message = self.db.query(Message).filter(Message.id == message_id).first()
        if not db_message:
            raise NotFoundException("Message not found")

        if db_message.author_id != user_id:
            raise ForbiddenException("Can only delete own messages")

        self.db.delete(db_message)
        self.db.commit()
