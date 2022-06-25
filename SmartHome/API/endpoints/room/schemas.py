from uuid import UUID
from pydantic import BaseModel
from ..device.schemas import Device


class CreateRoom(BaseModel):
    name: str

class PatchRoom(CreateRoom):
    pass

class RoomInfo(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True

class Room(RoomInfo):
    devices: list[Device]
