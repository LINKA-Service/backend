from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChannelBase(BaseModel):
    name: str
    description: Optional[str] = None


class ChannelCreate(ChannelBase):
    server_id: int


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ChannelResponse(ChannelBase):
    id: int
    server_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
