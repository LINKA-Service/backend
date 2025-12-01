from datetime import datetime, timedelta, timezone
from typing import List, Optional

import bcrypt
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.models.lawyer import Lawyer, LawyerReview
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
        self, lawyername: str, password: str
    ) -> Optional[Lawyer]:
        lawyer = (
            self.db.query(Lawyer).filter(Lawyer.lawyername == lawyername).first()
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

    def get_lawyer_by_lawyername(self, lawyername: str) -> Optional[Lawyer]:
        return (
            self.db.query(Lawyer).filter(Lawyer.lawyername == lawyername).first()
        )

    def get_lawyer_reviews(self, lawyername: str) -> List[LawyerReview]:
        lawyer = self.get_lawyer_by_lawyername(lawyername)
        if not lawyer:
            raise NotFoundException("Lawyer not found")
        return lawyer.reviews

    def create_review(self, review: LawyerReviewCreate) -> LawyerReview:
        lawyer = self.get_lawyer_by_lawyername(review.lawyername)
        if not lawyer:
            raise NotFoundException("Lawyer not found")

        db_review = LawyerReview(
            lawyername=review.lawyername,
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
        self, lawyer_id: int, lawyername_update: LawyernameUpdate
    ) -> Lawyer:
        db_lawyer = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
        if not db_lawyer:
            raise NotFoundException("Lawyer not found")

        setattr(db_lawyer, "lawyername", lawyername_update.lawyername)
        setattr(db_lawyer, "lawyername_changed_at", datetime.now(timezone.utc))

        self.db.commit()
        self.db.refresh(db_lawyer)
        return db_lawyer
