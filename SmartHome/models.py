from __future__ import typing
from ABC import ABC
from enum import Enum

from General import Identifable, UUID

class NamedIdentifable(Identifable, ABC):
    name: str

class User(NamedIdentifable):
    pass

class House(NamedIdentifable):
    owner_id: UUID

class Room(NamedIdentifable):
    pass

class Device(NamedIdentifable):
    urdi: bytes
    room_id: UUID
    model_id: UUID

class DeviceModel(NamedIdentifable):
    pass

class Parameter(NamedIdentifable):
    type: ParameterType

class ParameterType(enum):

    bool = 'bool'
    percentage = 'percentage'

    @property
    def valueType(self) -> class:
        match self:
            case ParameterType.bool:
                return bool
            case ParameterType.percentage:
                return float

    def toByte(value: Parameter.type.valueType) -> byte:
        match self:
            case ParameterType.bool:
                return 0x01 if value else 0x00
            case ParameterType.percentage:
                return int(value * 255).to_bytes(1, byteorder = 'big')
