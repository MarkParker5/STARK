from typing import Any
from enum import Enum
from pydantic import BaseModel


class SocketType(str, Enum):
    merlin = 'merlin'

class SocketData(BaseModel):
    type: SocketType
    data: dict[str, Any]

class MerlinData(BaseModel):
    device_id: str
    parameter_id: str
    value: str
