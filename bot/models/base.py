from db import Base
from sqlalchemy import Column, Integer, DateTime
import datetime

class BaseModel(Base):
    __abstract__ = True
  
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    create_at = Column(DateTime, nullable=False, default=datetime.datetime.now)