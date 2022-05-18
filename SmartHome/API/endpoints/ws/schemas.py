from typing import Any
from enum import Enum
from pydantic import BaseModel


class SocketType(str, Enum):
    merlin = 'merlin'
    merlin_raw = 'merlin_raw'

class SocketData(BaseModel):
    type: SocketType
    data: dict[str, Any]

class MerlinData(BaseModel):
    device_id: str
    parameter_id: str
    value: str

class MerlinRaw(BaseModel):
    urdi: int
    f: int
    x: int
