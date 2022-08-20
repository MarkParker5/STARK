from uuid import UUID
from pydantic import BaseModel
from .device import Device


class RoomCreate(BaseModel):
    name: str

class RoomPatch(RoomCreate):
    pass

class RoomInfo(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True

class Room(RoomInfo):
    devices: list[Device]
