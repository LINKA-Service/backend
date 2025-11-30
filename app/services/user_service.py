from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.schemas.user import ProfileUpdate, UsernameUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def update_profile(self, user_id: int, profile_update: ProfileUpdate) -> User:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise NotFoundException("User not found")

        update_data = profile_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_username(self, user_id: int, username_update: UsernameUpdate) -> User:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise NotFoundException("User not found")

        setattr(db_user, "username", username_update.username)
        setattr(db_user, "username_changed_at", datetime.now(timezone.utc))

        self.db.commit()
        self.db.refresh(db_user)
        return db_user
