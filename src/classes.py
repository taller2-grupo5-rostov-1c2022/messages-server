from pydantic import BaseModel
from typing import Optional, List


class PlayList(BaseModel):
    songs: List[str]


class User(BaseModel):
    songs: List[str]
    playlists: List[PlayList]


class UserUpdate(BaseModel):
    songs: Optional[List[str]] = None
    playlists: Optional[List[PlayList]] = None
