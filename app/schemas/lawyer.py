from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class LawyerBase(BaseModel):
    lawyername: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    specializations: List[str] = []


class LawyerCreate(LawyerBase):
    password: str


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    specializations: Optional[List[str]] = None


class LawyernameUpdate(BaseModel):
    lawyername: str


class LawyerResponse(BaseModel):
    id: int
    lawyername: str
    display_name: Optional[str] = None
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
    lawyername: str
    review: str


class LawyerReviewResponse(BaseModel):
    id: int
    lawyername: str
    review: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusResponse(BaseModel):
    message: str
