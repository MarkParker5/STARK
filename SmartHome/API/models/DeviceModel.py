from uuid import uuid1
from sqlalchemy import Table, Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from .Base import Base


class DeviceModelParameter(Base):
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1) # TODO: remove
    devicemodel_id = Column(ForeignKey('devicemodels.id'), primary_key = True)
    parameter_id = Column(ForeignKey('parameters.id'), primary_key = True)
    f = Column(Integer, nullable = False, default = 0)
    parameter = relationship('Parameter', lazy='joined')
    devicemodel = relationship('DeviceModel')
    __table_args__ = (UniqueConstraint('devicemodel_id', 'parameter_id'),)

    def __str__(self):
        return self.parameter.name or super().__str__()

class DeviceModel(Base):
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    name = Column(String)
    parameters = relationship('DeviceModelParameter', back_populates = 'devicemodel', cascade = 'all, delete-orphan', lazy = 'joined')

    def __str__(self):
        return self.name or super().__str__()
