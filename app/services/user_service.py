from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise NotFoundException("User not found")

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user
