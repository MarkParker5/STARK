from uuid import uuid1
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from .Base import Base


_devicemodelparameters = Table('devicemodelparameters', Base.metadata,
    Column('device_model_id', ForeignKey('devicemodels.id')),
    Column('parameter_id', ForeignKey('parameters.id')),
)

class DeviceModel(Base):
    id = Column(UUIDType, index = True, primary_key = True, default = uuid1)
    name = Column(String)
    parameters = relationship('Parameter', secondary = _devicemodelparameters)

    def __str__(self):
        return self.name or super().__str__()
