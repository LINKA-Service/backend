from datetime import datetime, timedelta, timezone
from typing import List, Optional

import bcrypt
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.models.lawyer import Lawyer, LawyerReview
from app.models.user import User
from app.schemas.lawyer import LawyerCreate, LawyerReviewCreate, LawyernameUpdate, ProfileUpdate


class LawyerService:
    def __init__(self, db: Session):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except ValueError:
            return False

    def get_password_hash(self, password: str) -> str:
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd_bytes, salt)
        return hashed_password.decode("utf-8")

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt

    def authenticate_lawyer(
        self, username: str, password: str
    ) -> Optional[Lawyer]:
        lawyer = (
            self.db.query(Lawyer).filter(Lawyer.username == username).first()
        )
        if not lawyer:
            return None
        if not self.verify_password(password, lawyer.hashed_password):
            return None
        return lawyer

    def create_lawyer(self, lawyer: LawyerCreate) -> Lawyer:
        hashed_password = self.get_password_hash(lawyer.password)
        db_lawyer = Lawyer(
            lawyername=lawyer.lawyername,
            hashed_password=hashed_password,
            display_name=lawyer.display_name,
            bio=lawyer.bio,
            avatar_url=lawyer.avatar_url,
            specializations=lawyer.specializations,
        )
        self.db.add(db_lawyer)
        self.db.commit()
        self.db.refresh(db_lawyer)
        return db_lawyer

    def change_password(
        self, lawyer_id: int, current_password: str, new_password: str
    ) -> bool:
        lawyer = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
        if not lawyer:
            raise UnauthorizedException("Lawyer not found")

        if not self.verify_password(current_password, lawyer.hashed_password):
            raise UnauthorizedException("Current password is incorrect")

        lawyer.hashed_password = self.get_password_hash(new_password)

        self.db.commit()
        return True

    def get_lawyer_by_username(self, username: str) -> Optional[Lawyer]:
        return (
            self.db.query(Lawyer).filter(Lawyer.username == username).first()
        )

    def get_lawyer_reviews(self, username: str) -> List[LawyerReview]:
        lawyer = self.get_lawyer_by_username(username)
        if not lawyer:
            raise NotFoundException("Lawyer not found")
        return lawyer.reviews

    def create_review(self, review: LawyerReviewCreate, username: str, current_user: User) -> LawyerReview:
        lawyer = self.get_lawyer_by_username(username)
        if not lawyer:
            raise NotFoundException("Lawyer not found")

        db_review = LawyerReview(
            lawyer_id=lawyer.id,
            author_id=current_user.id,
            review=review.review,
        )
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)
        return db_review

    def update_profile(self, lawyer_id: int, profile_update: ProfileUpdate) -> Lawyer:
        db_lawyer = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
        if not db_lawyer:
            raise NotFoundException("Lawyer not found")

        update_data = profile_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_lawyer, field, value)

        self.db.commit()
        self.db.refresh(db_lawyer)
        return db_lawyer

    def update_lawyername(
        self, lawyer_id: int, lawyer_name_update: LawyerNameUpdate
    ) -> Lawyer:
        db_lawyer = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
        if not db_lawyer:
            raise NotFoundException("Lawyer not found")

        setattr(db_lawyer, "lawyer_name", lawyer_name_update.lawyer_name)

        self.db.commit()
        self.db.refresh(db_lawyer)
        return db_lawyer
