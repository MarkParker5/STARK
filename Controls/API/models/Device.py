from uuid import uuid1
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from .Base import Base


class Device(Base):
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    name = Column(String)
    urdi = Column(Integer)
    room_id = Column(UUIDType, ForeignKey('rooms.id'))
    model_id = Column(UUIDType, ForeignKey('devicemodels.id'))
    room = relationship('Room', back_populates = 'devices')
    model = relationship('DeviceModel')

    def __str__(self):
        return self.name or super().__str__()
