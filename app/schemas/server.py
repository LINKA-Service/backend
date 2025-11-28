from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ServerBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None


class ServerResponse(ServerBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServerWithChannels(ServerResponse):
    channels: List['ChannelResponse'] = []

    class Config:
        from_attributes = True


# Import to resolve forward reference
from .channel import ChannelResponse
ServerWithChannels.model_rebuild()
