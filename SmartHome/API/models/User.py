from uuid import uuid1
from sqlalchemy import Column, String
from sqlalchemy_utils import UUIDType
from .Base import Base


class User(Base):
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    name = Column(String)
