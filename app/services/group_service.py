from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.group import Group, GroupMessage
from app.models.user import User
from app.schemas.group import GroupCreate, GroupUpdate
from app.schemas.message import MessageCreate


class GroupService:
    def __init__(self, db: Session):
        self.db = db

    def create_group(self, group: GroupCreate, owner_id: int) -> Group:
        db_group = Group(
            name=group.name,
            description=group.description,
            icon_url=group.icon_url,
            owner_id=owner_id,
        )
        self.db.add(db_group)
        self.db.commit()
        self.db.refresh(db_group)

        owner = self.db.query(User).filter(User.id == owner_id).first()
        if not owner:
            raise NotFoundException("Owner user not found")
        db_group.members.append(owner)
        self.db.commit()             
        self.db.refresh(db_group)

        return db_group

    def get_group(self, group_id: int) -> Optional[Group]:
        return self.db.query(Group).filter(Group.id == group_id).first()

    def get_user_groups(self, user_id: int) -> List[Group]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return user.groups

    def update_group(
        self, group_id: int, group_update: GroupUpdate, user_id: int
    ) -> Group:
        db_group = self.db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            raise NotFoundException("Group not found")

        if db_group.owner_id != user_id:
            raise ForbiddenException("Only group owner can update")

        update_data = group_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_group, field, value)

        self.db.commit()
        self.db.refresh(db_group)
        return db_group

    def delete_group(self, group_id: int, user_id: int) -> None:
        db_group = self.db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            raise NotFoundException("Group not found")

        if db_group.owner_id != user_id:
            raise ForbiddenException("Only group owner can delete")

        self.db.delete(db_group)
        self.db.commit()

    def join_group(self, group_id: int, user_id: int) -> Group:
        db_group = self.db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            raise NotFoundException("Group not found")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")
        if user in db_group.members:
            raise ForbiddenException("Already a member")

        db_group.members.append(user)
        self.db.commit()
        self.db.refresh(db_group)
        return db_group

    def leave_group(self, group_id: int, user_id: int) -> None:
        db_group = self.db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            raise NotFoundException("Group not found")

        if db_group.owner_id == user_id:
            raise ForbiddenException("Owner cannot leave group")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")
        if user not in db_group.members:
            raise ForbiddenException("Not a member")

        db_group.members.remove(user)
        self.db.commit()

    def is_group_member(self, group_id: int, user_id: int) -> bool:
        db_group = self.db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            return False

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        return user in db_group.members

    def create_message(self, message: MessageCreate, author_id: int) -> GroupMessage:
        db_message = GroupMessage(
            content=message.content, group_id=message.group_id, author_id=author_id
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_group_messages(
        self, group_id: int, skip: int = 0, limit: int = 50
    ) -> List[GroupMessage]:
        return (
            self.db.query(GroupMessage)
            .filter(GroupMessage.group_id == group_id)
            .order_by(GroupMessage.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_message(self, message_id: int, user_id: int) -> None:
        db_message = (
            self.db.query(GroupMessage).filter(GroupMessage.id == message_id).first()
        )
        if not db_message:
            raise NotFoundException("Message not found")

        if db_message.author_id != user_id:
            raise ForbiddenException("Can only delete own messages")

        self.db.delete(db_message)
        self.db.commit()
