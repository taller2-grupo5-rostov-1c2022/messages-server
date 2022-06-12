import json
from datetime import datetime
from typing import Any

from pydantic.main import BaseModel
from pydantic.utils import GetterDict


class UserBase(BaseModel):
    id: str


class MessageText(BaseModel):
    text: str


class MessageInfo(BaseModel):
    text: str
    sender: UserBase
    receiver: UserBase


class MessageGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == "sender":
            return UserBase(id=self._obj["sender_id"])
        if key == "receiver":
            return UserBase(id=self._obj["receiver_id"])
        try:
            return self._obj[key]
        except KeyError:
            return default


class MessageBase(MessageInfo):
    created_at: datetime


class MessageGet(MessageBase):
    id: int

    class Config:
        orm_mode = True
        getter_dict = MessageGetter


class MessagePost(BaseModel):
    sender_id: str
    receiver_id: str
    text: str
    created_at: datetime
