from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None


class GroupResponse(GroupBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GroupWithMembers(GroupResponse):
    member_count: int
