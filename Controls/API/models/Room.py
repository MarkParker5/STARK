from uuid import uuid1
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from .Base import Base


class Room(Base):
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    name = Column(String)
    house_id = Column(UUIDType, ForeignKey('houses.id'))
    house = relationship('House', back_populates = 'rooms')
    devices = relationship('Device', back_populates = 'room', cascade = 'all, delete-orphan')

    def __str__(self):
        return self.name or super().__str__()
