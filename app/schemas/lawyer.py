from datetime import datetime
from locale import str
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models import CaseType


class LawyerBase(BaseModel):
    lawyer_id: str
    lawyer_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    specializations: List[str] = []


class LawyerCreate(LawyerBase):
    password: str


class ProfileUpdate(BaseModel):
    lawyer_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    specializations: Optional[List[str]] = None


class LawyerIdUpdate(BaseModel):
    lawyer_id: str


class LawyerResponse(BaseModel):
    id: int
    lawyer_id: str
    lawyer_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    specializations: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LawyerToken(BaseModel):
    access_token: str
    token_type: str


class LawyerTokenData(BaseModel):
    lawyer_id: Optional[int] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class LawyerReviewCreate(BaseModel):
    review: str


class LawyerReviewResponse(BaseModel):
    id: int
    lawyer_id: str
    author_id: str
    case_type: CaseType
    review: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusResponse(BaseModel):
    message: str
