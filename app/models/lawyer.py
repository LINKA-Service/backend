import enum
from datetime import datetime, timezone

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.database import Base


class LawyerSpecialization(str, enum.Enum):
    SMISHING = "smishing"  # 스미싱 사기
    FALSE_ADVERTISING = "false_advertising"  # 허위 광고 사기
    SECONDHAND_FRAUD = "secondhand_fraud"  # 중고거래 사기
    INVESTMENT_SCAM = "investment_scam"  # 투자 유인 사기
    ACCOUNT_TAKEOVER = "account_takeover"  # 계정 도용 사기
    OTHER = "other"  # 기타


lawyer_groups = Table(
    "lawyer_groups",
    Base.metadata,
    Column("lawyer_id", Integer, ForeignKey("lawyers.id", ondelete="CASCADE")),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
)


class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    lawyername = Column(String, unique=True, index=True, nullable=False)
    lawyername_changed_at = Column(DateTime(timezone=True), nullable=True)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    specializations = Column(ARRAY(String), nullable=False, default=list)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    groups = relationship("Group", secondary=lawyer_groups, back_populates="lawyer_members")
    group_messages = relationship(
        "GroupMessage", back_populates="lawyer_author", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "LawyerReview", back_populates="lawyer", cascade="all, delete-orphan"
    )


class LawyerReview(Base):
    __tablename__ = "lawyer_reviews"

    id = Column(Integer, primary_key=True, index=True)
    lawyername = Column(
        String, ForeignKey("lawyers.lawyername", ondelete="CASCADE"), nullable=False, index=True
    )
    review = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    lawyer = relationship("Lawyer", back_populates="reviews")
