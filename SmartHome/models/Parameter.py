from uuid import uuid1
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from .Base import Base


class Parameter(Base):  # TODO: remove
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    name = Column(String, nullable = False)
    value_type = Column(String, nullable = False)
    device_parameters = relationship('DeviceParameterAssociation', back_populates = 'parameter', cascade = 'all, delete-orphan')
    devicemodel_parameters = relationship('DeviceModelParameter', back_populates = 'parameter', cascade = 'all, delete-orphan')

    def __str__(self):
        return self.name or super().__str__()
