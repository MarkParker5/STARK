from uuid import uuid1
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from .Base import Base


class Hub(Base):
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    name = Column(String)
    house_id = Column(UUIDType, ForeignKey('houses.id'))
    house = relationship('House', back_populates = 'hubs')

    def __str__(self):
        return self.name or super().__str__()
