from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from .base import BaseModel
from typing import Optional
from .users import User
import datetime


class Photo(BaseModel):
    __tablename__ = 'photos'
    photo_path: str = Column(String)
    user_create_id: Optional[User] = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    likes: int = Column(Integer, default=0)