from pydantic import BaseModel
from datetime import datetime


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    channel_id: int


class MessageResponse(MessageBase):
    id: int
    channel_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageWithAuthor(MessageResponse):
    author_username: str

    class Config:
        from_attributes = True
