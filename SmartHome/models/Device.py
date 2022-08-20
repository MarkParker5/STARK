from uuid import uuid1
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from .Base import Base


class DeviceParameterAssociation(Base):  # TODO: remove
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    device_id = Column(ForeignKey('devices.id'), primary_key = True)
    parameter_id = Column(ForeignKey('parameters.id'), primary_key = True)
    value = Column(Integer, nullable = False, default = 0)
    parameter = relationship('Parameter', lazy = 'selectin')
    device = relationship('Device')
    __table_args__ = (UniqueConstraint('device_id', 'parameter_id'),)

    def __str__(self):
        try:
            return self.parameter.name or super().__str__()
        except:
            return super().__str__()

class Device(Base):
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    name = Column(String)
    urdi = Column(Integer, unique = True, nullable = False)
    room_id = Column(UUIDType, ForeignKey('rooms.id'), nullable = False)
    model_id = Column(UUIDType, ForeignKey('devicemodels.id'), nullable = False)
    room = relationship('Room', back_populates = 'devices')
    model = relationship('DeviceModel', lazy = 'selectin')
    parameters = relationship('DeviceParameterAssociation', back_populates = 'device', cascade = 'all, delete-orphan')

    def __str__(self):
        return self.name or super().__str__()
