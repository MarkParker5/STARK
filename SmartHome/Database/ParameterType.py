from __future__ import typing
from ABC import ABC
from enum import Enum

class ParameterType(Enum):

    bool = 'bool'
    percentage = 'percentage'

    @property
    def valueType(self) -> class:
        match self:
            case ParameterType.bool:
                return bool
            case ParameterType.percentage:
                return float

    def toByte(value: valueType) -> byte:
        match self:
            case ParameterType.bool:
                return 0x01 if value else 0x00
            case ParameterType.percentage:
                return int(value * 255).to_bytes(1, byteorder = 'big')
