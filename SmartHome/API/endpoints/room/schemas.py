from uuid import UUID
from pydantic import BaseModel
from ..device.schemas import Device


class CreateRoom(BaseModel):
    name: str

class PatchRoom(CreateRoom):
    pass

class Room(BaseModel):
    id: UUID
    name: str
    devices: list[Device]

    class Config:
        orm_mode = True
