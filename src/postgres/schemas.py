from datetime import datetime

from pydantic.main import BaseModel
from typing import Optional, List


class UserBase(BaseModel):
    id: str

    class Config:
        orm_mode = True


class MessageText(BaseModel):
    text: str

    class Config:
        orm_mode = True


class MessageInfo(BaseModel):
    text: str
    sender: UserBase
    receiver: UserBase

    class Config:
        orm_mode = True


class MessageBase(MessageInfo):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class MessagePost(BaseModel):
    sender_id: str
    receiver_id: str
    text: str

    class Config:
        orm_mode = True
