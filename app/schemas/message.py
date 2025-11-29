from datetime import datetime

from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    group_id: int


class MessageResponse(MessageBase):
    id: int
    group_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageWithAuthor(MessageResponse):
    author_username: str
    author_display_name: str
    author_avatar_url: str
