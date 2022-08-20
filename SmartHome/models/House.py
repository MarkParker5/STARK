from uuid import uuid1
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from .Base import Base


class House(Base):
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    name = Column(String)
    hubs = relationship('Hub', back_populates = 'house', cascade = 'all, delete-orphan', lazy = 'selectin')
    rooms = relationship('Room', back_populates = 'house', cascade = 'all, delete-orphan', lazy = 'selectin')

    def __str__(self):
        return self.name or super().__str__()
