from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class LawyerBase(BaseModel):
    username: str
    lawyer_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    specializations: List[str] = []


class LawyerCreate(LawyerBase):
    username: str
    password: str


class ProfileUpdate(BaseModel):
    lawyer_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    specializations: Optional[List[str]] = None


class LawyerNameUpdate(BaseModel):
    lawyer_name: str


class LawyerResponse(BaseModel):
    id: int
    username: str
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
    username: str
    review: str


class LawyerReviewResponse(BaseModel):
    id: int
    username: str
    review: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusResponse(BaseModel):
    message: str
